import numpy as np
import operator
import itertools

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Plane
from compas.geometry import Polyline

from compas.datastructures import Mesh

from compas_slicer.geometry import Layer
from compas_slicer.geometry import Contour
from compas_slicer.geometry import PrintPoint

from compas_cgal.slicer import slice_mesh

__all__ = ['create_planar_contours_cgal']


def create_planar_contours_cgal(mesh, layer_height):
    """Creates planar contours using CGAL

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        A compas mesh.
    layer_height : float
        A number representing the height between cutting planes.
    """

    # get min and max z coordinates and determine number of layers
    bbox = mesh.bounding_box()
    x, y, z = zip(*bbox)
    min_z, max_z = min(z), max(z)
    d = abs(min_z - max_z)
    no_of_layers = int(d / layer_height) + 1

    normal = Vector(0, 0, 1)
    layers = []
    planes = []
    contours_per_layer = []

    # prepare mesh for slicing
    M = mesh.to_vertices_and_faces()

    # generate planes
    planes = [Plane(Point(0, 0, min_z + i * layer_height), normal) for i in range(no_of_layers)]

    # slicing operation
    contours = slice_mesh(M, planes)

    def get_grouped_list(item_list, key_function):
        # first sort, because grouping only groups consecutively matching items
        sorted_list = sorted(item_list, key=key_function)
        # group items, using the provided key function
        grouped_iter = itertools.groupby(sorted_list, key_function)
        # return reformatted list
        return [list(group) for _key, group in grouped_iter]

    def key_function(item):
        return item[0][2]

    grouped_contours = get_grouped_list(contours, key_function=key_function)
    
    for layer in grouped_contours:
        contours_per_layer = []
        for contour in layer:
            points_per_contour = []
            for point in contour:
                p = Point(point[0], point[1], point[2])
                points_per_contour.append(p)
            # generate contours
            # TODO: add a check for is_closed
            c = Contour(points=points_per_contour, is_closed=True)
            contours_per_layer.append(c)
        
        # generate layers
        l = Layer(contours_per_layer, None, None)
        layers.append(l)

    return layers

if __name__ == "__main__":
    pass
