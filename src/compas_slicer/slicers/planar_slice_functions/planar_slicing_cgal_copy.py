import numpy as np

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Plane
from compas.geometry import Polyline

from compas.datastructures import Mesh

from compas_slicer.geometry import Contour
from compas_slicer.geometry import Layer
from compas_slicer.geometry import PrintPoint

from compas_cgal.slicer import slice_mesh

__all__ = ['create_planar_contours_cgal_copy']


def create_planar_contours_cgal_copy(mesh, layer_height):
    ###########
    ### WIP ###
    ###########
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

    for i in range(no_of_layers):
        # define plane
        plane = Plane(Point(0, 0, min_z + i * layer_height), normal)
        planes.append(plane)

    # slicing operation per layer
    contour = slice_mesh(M, planes)

    count = 0
    print("len contour", len(contour))
    
    for j in range(len(contour)):
        if count >= len(contour):
            print("BREAK")
            break
        print("Contour #", count)
        points_current = contour[count]
        if count+1 < len(contour):
            points_next = contour[count+1]
        else:
            points_next = contour[count]

        z_current = points_current[0][2]
        z_next = points_next[0][2]

        print("current", points_current)
        print("next", points_next)

        contours_per_layer = []
        while z_next == z_current:
            print("SAME LAYER")
            print(count)
            points_current = contour[count]
            if count+1 < len(contour):
                points_next = contour[count+1]
            else:
                points_next = contour[count]

            z_current = points_current[0][2]
            z_next = points_next[0][2]

            is_closed = True
            c = Contour(points=points_current, is_closed=is_closed)
            contours_per_layer.append(c)
            count += 1

        layer = Layer(contours_per_layer, None, None)
        layers.append(layer)
        print("NEW LAYER")
        count += 1
        # contours_layer = []
        # print(j)
        # print(points[0][2])
        
        # TODO: implement the is_closed functionality
        
        # contours_per_layer.append(c)

        # layer = Layer(contours_per_layer, None, None)
        # layers.append(layer)
    return layers


if __name__ == "__main__":
    pass
