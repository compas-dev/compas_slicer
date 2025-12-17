from __future__ import annotations

from typing import TYPE_CHECKING

from compas.geometry import Point
from compas_cgal.polylines import simplify_polylines
from loguru import logger

if TYPE_CHECKING:
    from compas_slicer.slicers import BaseSlicer


__all__ = ["simplify_paths_rdp"]


def simplify_paths_rdp(slicer: BaseSlicer, threshold: float) -> None:
    """Simplify paths using the Ramer-Douglas-Peucker algorithm.

    Uses CGAL Polyline_simplification_2 implementation.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    threshold: float
        Controls the degree of polyline simplification.
        Low threshold removes few points, high threshold removes many points.

    References
    ----------
    https://en.wikipedia.org/wiki/Ramer-Douglas-Peucker_algorithm
    """
    logger.info("Paths simplification rdp (CGAL)")
    remaining_pts_num = 0

    for layer in slicer.layers:
        if layer.is_raft:
            continue

        polylines = [[[pt[0], pt[1], pt[2]] for pt in path.points] for path in layer.paths]
        simplified = simplify_polylines(polylines, threshold)

        for path, pts_simplified in zip(layer.paths, simplified):
            path.points = [Point(pt[0], pt[1], pt[2]) for pt in pts_simplified]
            remaining_pts_num += len(path.points)

    logger.info(f"{remaining_pts_num} points remaining after simplification")
