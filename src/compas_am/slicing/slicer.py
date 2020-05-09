import compas
from compas.datastructures import Mesh, mesh_contours_numpy
from compas.geometry import  Point, distance_point_point

import numpy as np

from compas_am.slicing.printpath import Contour
from compas_am.slicing.printpath import Layer
import compas_am.slicing.curved_slicing as curved_slicing
import compas_am.slicing.adaptive_slicing as adaptive_slicing
import compas_am.slicing.planar_slicing as planar_slicing
from compas_am.utilities import utils
from compas_am.sorting.sort_shortest_path import sort_shortest_path
from compas_am.sorting.sort_per_segment import sort_per_segment
from compas_am.sorting.seams_align import seams_align
from compas_am.sorting.seams_random import seams_random

import logging
logger = logging.getLogger('logger')

class Slicer:
    """
    Slicer class is an organizational class that holds all the information for the slice process
    It does not implement functions, but rather links to the implementation in other parts of the compas_am library 
    Should be kept as clean and short as possible 
    
    Attributes
    ----------
    mesh : compas.datastructures.Mesh 
        Input mesh
    slicer_type : str
        "planar_numpy", "planar_meshcut", "curved", "adaptive"
    layer_height : float
        Layer height only valid for planar slicing 
        TODO: find a solution for input for adaptive and curved slicing 

    """

    def __init__(self, mesh, slicer_type = "planar", layer_height = 2.0):
        ## check input
        assert isinstance(mesh, compas.datastructures.Mesh), "Input mesh has to be of type <compas.datastructures.Mesh>, yours is of type: "+str(type(mesh))
        self.check_triangular_mesh(mesh)

        ### input
        self.mesh = mesh
        self.layer_height = layer_height
        self.slicer_type = slicer_type

        ### Print paths grouped per height level in Layer classes
        self.layers = [] # class Layer. Horizontally arranged and not sorted in any way. Direct result of the slicing algorithm

        ### Print paths sorted by selected sorting algorithm
        self.sorted_paths = [] # any class inheriting from SortedPathCollection, i.e. Segment (vertical sorting) or Layer(horizontal sorting)


    ##############################
    ### --- Slicing 
    def slice_model(self, create_contours, create_infill, create_supports):
        if create_contours:
            self.generate_contours()

        if create_infill:
            self.generate_infill()

        if create_supports:
            self.generate_supports()

    ### --- Contours
    def generate_contours(self):
        if self.slicer_type == "planar_numpy":
            logger.info("Planar contours compas numpy slicing")
            self.layers = planar_slicing.create_planar_contours_numpy(self.mesh, self.layer_height)

        elif self.slicer_type == "planar_meshcut":
            logger.info("Planar contours meshcut slicing")
            self.layers = planar_slicing.create_planar_contours_meshcut(self.mesh, self.layer_height)

        elif self.slicer_type == "curved":
            self.layers = curved_slicing.create_curved_contours(mesh, boundaries = None, min_layer_height = None, max_layer_height = None)

        elif self.slicer_type == "adaptive":
            self.layers = adaptive_slicing.create_adaptive_height_contours(mesh, min_layer_height = None, max_layer_height = None)

        else: 
            raise NameError("Invalid slicing type : " + slicer_type)


    ##############################
    ### --- Polyline Simplification

    def simplify_paths(self, method, threshold, iterations = 1):
        logger.info("Paths simplification, method : " + method)

        if method == "uniform" or method == "all":
            for layer in self.layers:
                [path.simplify_uniform(threshold) for path in layer.get_all_paths()]
        if method == "curvature_adapted" or method == "all":
            for layer in self.layers:
                [path.simplify_adapted_to_curvature(threshold, iterations) for path in layer.get_all_paths()]
        if method !="uniform" and method !="curvature_adapted" and method !="all" :
            raise NameError("Invalid polyline simplification method : " + method)



    ##############################
    ### --- Sorting paths

    def sort_paths(self, method, population_size=200, mutation_probability=0.1, max_attempts=10, random_state=None):
        logger.info("Sorting paths, method : " + method )
        if method == "shortest_path":
            logger.info("max_attempts : " + str(max_attempts))
            self.sorted_paths = sort_shortest_path(self.layers, population_size, mutation_probability, max_attempts, random_state)
        elif method == "per_segment":
            self.sorted_paths = sort_per_segment(self.layers, d_threshold = self.layer_height * 1.4)
        else: 
            raise NameError("Invalid sorting method : " + method)

    ##############################
    ### --- Seam alignment

    def align_seams(self, method):
        logger.info("Aligning seams, method : " + method)
        if method == "seams_align":
            self.layers = seams_align(self.layers)
        elif method == "seams_random":
            self.layers = seams_random(self.layers)
        else: 
            raise NameError("Invalid seam alignment method : " + method)


    ##############################
    ### --- Output 

    def printout_info(self):
        open_contours = 0
        closed_contours = 0
        total_number_of_pts = 0
        number_of_layers = 0


        for layer in self.layers:
            number_of_layers +=1
            for contour in layer.contours:
                total_number_of_pts += len(contour.points)
                if contour.is_closed:
                    closed_contours +=1
                else: 
                    open_contours +=1

        print ("\n---- Slicer Info ----")
        print ("Slicer type : ", self.slicer_type)
        print ("Layer height: ", self.layer_height, " mm")
        print ("Number of layers: %d"% number_of_layers)
        print ("Number of contours: %d, open contours: %d, closed contours: %d"%(open_contours+closed_contours,open_contours, closed_contours))
        print ("Number of sampling points on contours: %d"% total_number_of_pts)
        print ("Paths have been sorted: "+ str(len(self.sorted_paths)>0) + "\n")


    def get_contour_lines_for_plotter(self, color = (255,0,0)):
        lines = []
        for layer in self.layers:
            for contour in layer.contours:
                lines.extend(contour.get_lines_for_plotter(color))
        return lines

    def save_contours_to_json(self, path, name):
        if len(self.sorted_paths) >0:
            paths_collection = self.sorted_paths
        else: 
            paths_collection = self.layers

        if len(paths_collection) == 0:
             raise TypeError("The paths_collection of the slicer is empty")

        data = {}
        count = 0
        for collection in paths_collection:
            for contour in collection.contours: 
                data[count] = [list(point) for point in contour.points]
                count += 1
        utils.save_to_json(data, path, name)

    ##############################
    ### --- Other 

    def check_triangular_mesh(self, mesh):
        for fkey in mesh.faces():
            vs = mesh.face_vertices(fkey)
            if len(vs)!=3:
                raise TypeError("Found a quad at face key: "+str(fkey)+" ,number of face vertices:"+str(len(vs))+". \nOnly triangular meshes supported. \
                                \nConsider using the Weaverbird's component 'Split Triangles Subdivision' to triangulate, and then remeber to weld the resulting mesh")

if __name__ == "__main__":
    pass       
        