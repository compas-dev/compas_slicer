from __future__ import annotations

from typing import TYPE_CHECKING

from compas.geometry import (
    add_vectors,
    distance_point_point_xy,
    intersection_line_line_xy,
    is_point_on_segment_xy,
    scale_vector,
)

from compas_slicer.slicers.slice_utilities import ContoursBase

if TYPE_CHECKING:
    from compas.datastructures import Mesh

__all__ = ["UVContours"]


class UVContours(ContoursBase):
    def __init__(self, mesh: Mesh, p1: tuple[float, float], p2: tuple[float, float]) -> None:
        ContoursBase.__init__(self, mesh)  # initialize from parent class
        self.p1 = p1  # tuple (u,v); first point in uv domain defining the cutting line
        self.p2 = p2  # tuple (u,v); second point in uv domain defining the cutting line

    def uv(self, vkey: int) -> tuple[float, float]:
        uv: tuple[float, float] = self.mesh.vertex[vkey]["uv"]
        return uv

    def edge_is_intersected(self, v1: int, v2: int) -> bool:
        """Returns True if the edge v1,v2 intersects the line in the uv domain, False otherwise."""
        p = intersection_line_line_xy((self.p1, self.p2), (self.uv(v1), self.uv(v2)))
        return bool(
            p
            and is_point_on_segment_xy(p, (self.uv(v1), self.uv(v2)))
            and is_point_on_segment_xy(p, (self.p1, self.p2))
        )

    def find_zero_crossing_data(self, v1: int, v2: int) -> list[float] | None:
        """Finds the position of the zero-crossing on the edge u,v."""
        p = intersection_line_line_xy((self.p1, self.p2), (self.uv(v1), self.uv(v2)))
        d1, d2 = distance_point_point_xy(self.uv(v1), p), distance_point_point_xy(self.uv(v2), p)
        if d1 + d2 > 0:
            vec = self.mesh.edge_vector(v1, v2)
            vec = scale_vector(vec, d1 / (d1 + d2))
            pt: list[float] = add_vectors(self.mesh.vertex_coordinates(v1), vec)
            return pt
        return None
