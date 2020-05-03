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

    def __init__(self, mesh, slicer_type = "planar", layer_height = 0.01):
        ### input
        self.mesh = mesh
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
        # WIP
        plane_origin = (0, 25, 0)
        plane_normal = (0, 0, 1)
        plane = meshcut.Plane(plane_origin, plane_normal)

        P = meshcut.cross_section_mesh(self.mesh, plane)

        for item in P:
            contours = item.tolist()
        
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
        print ("Number of contours: %d, open contours: %d, closed contours: %d"%(len(self.contours),open_contours, closed_contours))
        print ("Number of sampling points on contours: %d "% total_number_of_pts)
        print ("\n")

    def get_contour_lines_for_plotter(self, color = (255,0,0)):
        lines = []
        for contour in self.contours:
            lines.extend(contour.get_lines_for_plotter(color))
        return lines

    def save_contours_in_Json(self, path, name):
        data = {}
        for i,contour in enumerate(self.contours):
            data[i] = [list(point) for point in contour.points]
        utils.save_Json(data, path, name)

        
        