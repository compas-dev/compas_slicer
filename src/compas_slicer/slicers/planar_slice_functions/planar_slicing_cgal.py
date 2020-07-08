import sys

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Plane

from compas_slicer.geometry import Contour
from compas_slicer.geometry import Layer


try:
    from compas_cgal.slicer import slice_mesh
except:
    pass

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
    if not 'compas_cgal' in sys.modules:
        raise NameError('Attention! You need to install compas_cgal to use this function')

    # get min and max z coordinates and determine number of layers
    bbox = mesh.bounding_box()
    x, y, z = zip(*bbox)
    min_z, max_z = min(z), max(z)
    d = abs(min_z - max_z)
    no_of_layers = int(d / layer_height) + 1

    normal = Vector(0, 0, 1)
    layers = []

    # prepare mesh for slicing
    M = mesh.to_vertices_and_faces()

    for i in range(no_of_layers):
        contours_per_layer = []
        # define plane
        # OLD plane_origin = (0, 0, min_z + i * layer_height + 0.01)
        plane = Plane(Point(0, 0, min_z + i * layer_height), normal)

        # slicing operation per layer
        contour = slice_mesh(M, [plane])

        for points in contour:
            # TODO: implement the is_closed functionality
            is_closed = True
            c = Contour(points=points, is_closed=is_closed)
            contours_per_layer.append(c)

        layer = Layer(contours_per_layer, None, None)
        layers.append(layer)
    return layers


if __name__ == "__main__":
    pass
