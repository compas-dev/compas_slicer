from __future__ import annotations

from typing import TYPE_CHECKING

from compas.geometry import add_vectors, distance_point_point_xy, intersection_line_line_xy, scale_vector

from compas_slicer.slicers.slice_utilities import ContoursBase

if TYPE_CHECKING:
    from compas.datastructures import Mesh

__all__ = ['UVContours']


class UVContours(ContoursBase):
    def __init__(self, mesh: Mesh, p1: tuple[float, float], p2: tuple[float, float]) -> None:
        ContoursBase.__init__(self, mesh)  # initialize from parent class
        self.p1 = p1  # tuple (u,v); first point in uv domain defining the cutting line
        self.p2 = p2  # tuple (u,v); second point in uv domain defining the cutting line

    def uv(self, vkey: int) -> tuple[float, float]:
        uv: tuple[float, float] = self.mesh.vertex[vkey]['uv']
        return uv

    def edge_is_intersected(self, v1: int, v2: int) -> bool:
        """ Returns True if the edge v1,v2 intersects the line in the uv domain, False otherwise. """
        p = intersection_line_line_xy((self.p1, self.p2), (self.uv(v1), self.uv(v2)))
        return bool(p and is_point_on_line_xy(p, (self.uv(v1), self.uv(v2))) and is_point_on_line_xy(p, (self.p1, self.p2)))

    def find_zero_crossing_data(self, v1: int, v2: int) -> list[float] | None:
        """ Finds the position of the zero-crossing on the edge u,v. """
        p = intersection_line_line_xy((self.p1, self.p2), (self.uv(v1), self.uv(v2)))
        d1, d2 = distance_point_point_xy(self.uv(v1), p), distance_point_point_xy(self.uv(v2), p)
        if d1 + d2 > 0:
            vec = self.mesh.edge_vector(v1, v2)
            vec = scale_vector(vec, d1 / (d1 + d2))
            pt: list[float] = add_vectors(self.mesh.vertex_coordinates(v1), vec)
            return pt
        return None


# utility function

def is_point_on_line_xy(
    c: list[float] | tuple[float, ...],
    line: tuple[tuple[float, ...] | list[float], tuple[float, ...] | list[float]],
    epsilon: float = 1e-6,
) -> bool:
    """
    Not using the equivalent function of compas, because for some reason it always returns True.

    c: list that represents a point with 2 coordinates [x.y] of [x,y,0]
    line: (p1, p2) where each pt represents a point with 2 coordinates [x.y] of [x,y,0]
    """
    a, b = line[0], line[1]
    cross_product = (c[1] - a[1]) * (b[0] - a[0]) - (c[0] - a[0]) * (b[1] - a[1])

    if abs(cross_product) > epsilon:
        return False

    dot_product = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1]) * (b[1] - a[1])
    if dot_product < 0:
        return False

    squared_length_ba = (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1])
    return not dot_product > squared_length_ba


if __name__ == "__main__":
    pass
