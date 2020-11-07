from compas_slicer.slicers.slice_utilities import ZeroCrossingContoursBase
from compas.geometry import Vector, add_vectors, scale_vector

__all__ = ['GeodesicsZeroCrossingContours']


class GeodesicsZeroCrossingContours(ZeroCrossingContoursBase):
    """
    Finds the iso-contours of the function f(x) = vertex_data['distance']
    on the mesh.

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    """
    def __init__(self, mesh):
        ZeroCrossingContoursBase.__init__(self, mesh)  # initialize from parent class

    def edge_is_intersected(self, u, v):
        """ Returns True if the edge u,v has a zero-crossing, False otherwise. """
        d1 = self.mesh.vertex[u]['get_distance']
        d2 = self.mesh.vertex[v]['get_distance']
        if (d1 > 0 and d2 > 0) or (d1 < 0 and d2 < 0):
            return False
        else:
            return True

    def find_zero_crossing_point(self, u, v):
        """ Finds the position of the zero-crossing on the edge u,v. """
        dist_a, dist_b = self.mesh.vertex[u]['get_distance'], self.mesh.vertex[v]['get_distance']
        if abs(dist_a) + abs(dist_b) > 0:
            v_coords_a, v_coords_b = self.mesh.vertex_coordinates(u), self.mesh.vertex_coordinates(v)
            vec = Vector.from_start_end(v_coords_a, v_coords_b)
            vec = scale_vector(vec, abs(dist_a) / (abs(dist_a) + abs(dist_b)))
            pt = add_vectors(v_coords_a, vec)
            return pt


if __name__ == "__main__":
    pass
