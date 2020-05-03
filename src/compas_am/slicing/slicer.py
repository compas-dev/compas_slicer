import compas
from compas.datastructures import Mesh, mesh_contours_numpy
from compas.geometry import  Point, distance_point_point
from compas_am.slicing.printpath import Contour
from compas_am.utilities import utils
from compas_am.sorting.shortest_path_sorting import shortest_path_sorting
from compas_am.sorting.per_segment_sorting import per_segment_sorting

import meshcut

class Slicer:
    """
    Slicer class is an organizational class that holds all the information for the slice process
    It does not impliment functions, but rather links to the implementation in other parts of the compas_am library  
    
    Attributes
    ----------
    mesh         : <compas.datastructures.Mesh>
    slicer_type  : <str> "planar", "planar_meshcut", "curved", "adaptive"
    layer_height : <float> 
    """

    def __init__(self, mesh, min_z, max_z, slicer_type = "planar", layer_height = 0.01):
        ### input
        self.mesh = mesh
        self.min_z = min_z
        self.max_z = max_z
        self.layer_height = layer_height
        self.slicer_type = slicer_type

        ### print paths
        self.contours = []
        self.infill_paths = []
        self.support_paths = []


    ###############
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
        if self.slicer_type == "planar":
            self.contours = self.contours_planar()
        elif self.slicer_type == "planar_meshcut":
            self.contours = self.contours_planar_meshcut()   
        elif self.slicer_type == "curved":
            self.contours = self.contours_curved()
        elif self.slicer_type == "adaptive":
            self.contours = self.contours_adaptive()
        else: 
            raise "Invalid slicing type : " + slicer_type

    def contours_planar(self):
        z = [self.mesh.vertex_attribute(key, 'z') for key in self.mesh.vertices()]
        z_bounds = max(z) - min(z)
        levels = []
        p = min(z) 
        while p < max(z):
            levels.append(p)
            p += self.layer_height 

        levels, compound_contours = compas.datastructures.mesh_contours_numpy(self.mesh, levels=levels, density=10)
        
        contours = []
        for i, compound_contour in enumerate(compound_contours):
            for path in compound_contour:
                for polygon2d in path:
                    points = [Point(p[0], p[1], levels[i]) for p in polygon2d[:-1]]
                    if len(points)>0:
                        threshold_closed = 15.0 #TODO: VERY BAD!! Threshold should not be hardcoded
                        is_closed = distance_point_point(points[0], points[-1]) < threshold_closed
                        c = Contour(points = points, is_closed = is_closed)
                        contours.append(c)
        return contours

    def contours_planar_meshcut(self):
        # calculate number of layers needed
        d = abs(self.min_z - self.max_z)
        no_of_layers = int(d / self.layer_height)+1
      
        contours = []

        for i in range(no_of_layers):
            # define plane
            # TODO check if addding 0.01 tolerance makes sense
            plane_origin = (0, 0, self.min_z + i*self.layer_height + 0.01)
            plane_normal = (0, 0, 1)
            plane = meshcut.Plane(plane_origin, plane_normal)
            # cut using meshcut cross_section_mesh
            meshcut_array = meshcut.cross_section_mesh(self.mesh, plane)
            for item in meshcut_array:
                # convert np array to list
                # TODO needs to be optimised, tolist() is slow
                meshcut_list = item.tolist()
                points = [Point(p[0], p[1], p[2]) for p in meshcut_list]
                # append first point to form a closed polyline
                # TODO has to be improved
                points.append(points[0])
                # TODO is_closed is always set to True, has to be checked
                is_closed = True
                c = Contour(points = points, is_closed = is_closed)
                contours.append(c)
        return contours

    def contours_curved(self):
        raise NotImplementedError

    def contours_adaptive(self):
        raise NotImplementedError



    ### --- Infill
    def generate_infill(self):
        raise NotImplementedError


    ### --- Supports
    def generate_supports(self):
        raise NotImplementedError


    ##############################
    ### --- Polylines Simplification

    def simplify_paths(self, threshold):
        [path.simplify(threshold) for path in self.contours]
        [path.simplify(threshold) for path in self.infill_paths]
        [path.simplify(threshold) for path in self.support_paths]


    ##############################
    ### --- Sorting paths

    def sort_paths(self, sorting_type):
        if sorting_type == "shortest path":
            sorted_paths = shortest_path_sorting(self.contours, self.infill_paths, self.support_paths)
        elif sorting_type == "per segment":
            sorted_paths = per_segment_sorting(self.contours, self.infill_paths, self.support_paths)
        return sorted_paths


    ##############################
    ### --- Output 

    def printout_info(self):
        open_contours = 0
        closed_contours = 0
        total_number_of_pts = 0
        for c in self.contours:
            total_number_of_pts += len(c.points)
            if c.is_closed:
                closed_contours +=1
            else: 
                open_contours +=1

        print ("\n---- Slicer Info ----")
        print ("Slicer type : ", self.slicer_type)
        print ("Layer height: ", self.layer_height, " mm")
        print ("Number of contours: %d, open contours: %d, closed contours: %d"%(len(self.contours),open_contours, closed_contours))
        print ("Number of sampling points on contours: %d "% total_number_of_pts)
        print ("\n")

    def get_contour_lines_for_plotter(self, color = (255,0,0)):
        lines = []
        for contour in self.contours:
            lines.extend(contour.get_lines_for_plotter(color))
        return lines

    def save_contours_to_json(self, path, name):
        data = {}
        for i,contour in enumerate(self.contours):
            data[i] = [list(point) for point in contour.points]
        utils.save_to_json(data, path, name)

        
        