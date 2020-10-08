from compas.geometry import Plane, Point, Vector
from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer

__all__ = ['create_planar_paths']

def create_planar_paths(mesh, layer_height):
    """
    Creates planar contours using the compas.geometry.trimesh_slice function.

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        The mesh to be sliced
    layer_height : float
        A number representing the height between cutting planes.
    """

    ## TODO: To be tested with more complex shapes!
    z_heights = [mesh.vertex_attribute(key, 'z') for key in mesh.vertices()]
    layers = []
    z = min(z_heights)
    z += layer_height * 0.5
    while z < max(z_heights):
        print('Cutting at height %.3f' % z)

        plane = Plane(Point(0, 0, z), Vector(0, 0, 1))
        intersection_v_keys = IntersectionMeshPlane(mesh, plane).intersections

        points = []
        for key in intersection_v_keys:
            coords = mesh.vertex_coordinates(key, axes='xyz')
            point = Point(coords[0], coords[1], coords[2])
            points.append(point)

        path = Path(points=points, is_closed=True)
        layers.append(Layer([path]))
        z += layer_height
    return layers


###################################
### Intersect class
###################################

from compas.geometry import intersection_segment_plane
from compas.geometry import length_vector
from compas.geometry import subtract_vectors

"""
Part of this is a copied from compas.datastructures.core.cut
Contact Tom to find out how to properly import it from compas
"""

class IntersectionMeshPlane(object):

    def __init__(self, mesh, plane):
        self.mesh = mesh
        self.plane = plane
        self._intersections = []
        self.intersect()

    @property
    def intersections(self):
        return self._intersections

    @property
    def is_none(self):
        return len(self.intersections) == 0

    @property
    def is_point(self):
        return len(self.intersections) == 1

    @property
    def is_line(self):
        return len(self.intersections) == 2

    @property
    def is_polygon(self):
        return len(self.intersections) >= 3

    def intersect(self):
        intersections = []
        for u, v in list(self.mesh.edges()):
            a = self.mesh.vertex_attributes(u, 'xyz')
            b = self.mesh.vertex_attributes(v, 'xyz')
            x = intersection_segment_plane((a, b), self.plane)
            if not x:
                continue
            L_ax = length_vector(subtract_vectors(x, a))
            L_ab = length_vector(subtract_vectors(b, a))
            t = L_ax / L_ab
            key = self.mesh.split_edge(u, v, t=t, allow_boundary=True)
            intersections.append(key)
        self._intersections = intersections
