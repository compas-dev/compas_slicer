import compas
from compas.datastructures import Mesh, mesh_contours_numpy
from compas.geometry import  Point, distance_point_point
from compas_am.slicing.printpath import Contour
from compas_am.utilities import utils

class Slicer:
    def __init__(self, mesh, slicer_type = "regular", layer_height = 0.01):
        self.mesh = mesh
        self.layer_height = layer_height

        self.contours = []

        if slicer_type == "regular":
            self.contours = self.regular_geometry_slicing()
        elif slicer_type == "curved":
            raise NotImplementedError
        elif slicer_type == "adaptive height":
            raise NotImplementedError
        else: 
            raise "Invalid slicer type : " + slicer_type

    def regular_geometry_slicing(self):
        levels, compound_contours = compas.datastructures.mesh_contours_numpy(self.mesh, levels=None, density=10)
        
        contours = []
        for i, compound_contour in enumerate(compound_contours):
            for path in compound_contour:
                for polygon2d in path:
                    points = [Point(p[0], p[1], levels[i]) for p in polygon2d[:-1]]
                    if len(points)>0:
                        threshold_closed = 15.0 #TODO: VERY BAD!! Threshold should not be hardcoded
                        is_closed = distance_point_point(points[0], points[-1]) < threshold_closed
                        print (distance_point_point(points[0], points[-1]))
                        c = Contour(points = points, is_closed = is_closed)
                        print (is_closed)
                        contours.append(c)
        return contours


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
        
        