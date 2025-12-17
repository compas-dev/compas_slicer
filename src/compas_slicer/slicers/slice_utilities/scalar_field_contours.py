from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from compas.geometry import Point, Vector, add_vectors, scale_vector

from compas_slicer.slicers.slice_utilities import ContoursBase

if TYPE_CHECKING:
    from compas.datastructures import Mesh

__all__ = ["ScalarFieldContours"]


class ScalarFieldContours(ContoursBase):
    """
    Finds the iso-contours of the function f(x) = vertex_data['scalar_field']
    on the mesh.

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    """

    def __init__(self, mesh: Mesh) -> None:
        ContoursBase.__init__(self, mesh)  # initialize from parent class

    def find_intersections(self) -> None:
        """Vectorized intersection finding for scalar field contours.

        Overrides parent method for ~10x speedup on large meshes.
        """
        # Get all edges as numpy array
        edges = np.array(list(self.mesh.edges()))
        n_edges = len(edges)

        if n_edges == 0:
            return

        # Get scalar field values for all vertices
        scalar_field = np.array([self.mesh.vertex[v]["scalar_field"] for v in range(len(list(self.mesh.vertices())))])

        # Get scalar values at edge endpoints
        d1 = scalar_field[edges[:, 0]]
        d2 = scalar_field[edges[:, 1]]

        # Vectorized intersection test: sign change across edge
        intersected = (d1 * d2) <= 0  # different signs or zero

        # Get vertex coordinates
        vertices = np.array([self.mesh.vertex_coordinates(v) for v in self.mesh.vertices()])

        # Compute zero crossings for intersected edges
        intersected_edges = edges[intersected]
        d1_int = d1[intersected]
        d2_int = d2[intersected]

        # Interpolation parameter (avoid division by zero)
        abs_d1 = np.abs(d1_int)
        abs_d2 = np.abs(d2_int)
        denom = abs_d1 + abs_d2
        valid = denom > 0

        # Compute intersection points
        v1 = vertices[intersected_edges[:, 0]]
        v2 = vertices[intersected_edges[:, 1]]

        # Linear interpolation: pt = v1 + t * (v2 - v1) where t = |d1| / (|d1| + |d2|)
        t = np.zeros(len(intersected_edges))
        t[valid] = abs_d1[valid] / denom[valid]
        pts = v1 + t[:, np.newaxis] * (v2 - v1)

        # Store results
        for edge, pt, is_valid in zip(intersected_edges, pts, valid):
            if is_valid:
                edge_tuple = (int(edge[0]), int(edge[1]))
                rev_edge = (int(edge[1]), int(edge[0]))
                if edge_tuple not in self.intersection_data and rev_edge not in self.intersection_data:
                    self.intersection_data[edge_tuple] = Point(pt[0], pt[1], pt[2])

        # Build edge to index mapping
        for i, e in enumerate(self.intersection_data):
            self.edge_to_index[e] = i

    def edge_is_intersected(self, u: int, v: int) -> bool:
        """Returns True if the edge u,v has a zero-crossing, False otherwise."""
        d1 = self.mesh.vertex[u]["scalar_field"]
        d2 = self.mesh.vertex[v]["scalar_field"]
        return not (d1 > 0 and d2 > 0 or d1 < 0 and d2 < 0)

    def find_zero_crossing_data(self, u: int, v: int) -> list[float] | None:
        """Finds the position of the zero-crossing on the edge u,v."""
        dist_a, dist_b = self.mesh.vertex[u]["scalar_field"], self.mesh.vertex[v]["scalar_field"]
        if abs(dist_a) + abs(dist_b) > 0:
            v_coords_a, v_coords_b = self.mesh.vertex_coordinates(u), self.mesh.vertex_coordinates(v)
            vec = Vector.from_start_end(v_coords_a, v_coords_b)
            vec = scale_vector(vec, abs(dist_a) / (abs(dist_a) + abs(dist_b)))
            pt: list[float] = add_vectors(v_coords_a, vec)
            return pt
        return None


if __name__ == "__main__":
    pass
