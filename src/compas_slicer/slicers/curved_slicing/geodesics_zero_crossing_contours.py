from compas_slicer.slicers.slice_utilities import ZeroCrossingContours
from compas.geometry import Vector, add_vectors, scale_vector

__all__ = ['GeodesicsZeroCrossingContours']


class GeodesicsZeroCrossingContours(ZeroCrossingContours):
    def __init__(self, mesh):
        ZeroCrossingContours.__init__(self, mesh)  # initialize from parent class

    def edge_is_intersected(self, u, v):
        d1 = self.mesh.vertex[u]['distance']
        d2 = self.mesh.vertex[v]['distance']
        if (d1 > 0 and d2 > 0) or (d1 < 0 and d2 < 0):
            return False
        else:
            return True

    def find_zero_crossing_point(self, u, v):
        dist_a, dist_b = self.mesh.vertex[u]['distance'], self.mesh.vertex[v]['distance']
        if abs(dist_a) + abs(dist_b) > 0:
            v_coords_a, v_coords_b = self.mesh.vertex_coordinates(u), self.mesh.vertex_coordinates(v)
            vec = Vector.from_start_end(v_coords_a, v_coords_b)
            vec = scale_vector(vec, abs(dist_a) / (abs(dist_a) + abs(dist_b)))
            pt = add_vectors(v_coords_a, vec)
            return pt
