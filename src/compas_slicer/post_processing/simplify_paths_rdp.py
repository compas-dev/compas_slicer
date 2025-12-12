from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import rdp as rdp_py
from compas.geometry import Point
from loguru import logger

if TYPE_CHECKING:
    from compas_slicer.slicers import BaseSlicer


__all__ = ['simplify_paths_rdp']

# Check for CGAL availability at module load
_USE_CGAL = False
try:
    from compas_cgal.polylines import simplify_polylines as _cgal_simplify
    _USE_CGAL = True
except ImportError:
    _cgal_simplify = None


def simplify_paths_rdp(slicer: BaseSlicer, threshold: float) -> None:
    """Simplify paths using the Ramer-Douglas-Peucker algorithm.

    Uses CGAL native implementation if available (10-20x faster),
    otherwise falls back to Python rdp library.

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
    if _USE_CGAL:
        _simplify_paths_cgal(slicer, threshold)
    else:
        _simplify_paths_python(slicer, threshold)


def _simplify_paths_cgal(slicer: BaseSlicer, threshold: float) -> None:
    """Simplify paths using CGAL Polyline_simplification_2."""
    logger.info("Paths simplification rdp (CGAL)")
    remaining_pts_num = 0

    for layer in slicer.layers:
        if layer.is_raft:
            continue

        # Batch all paths in this layer for efficient CGAL processing
        polylines = [[[pt[0], pt[1], pt[2]] for pt in path.points] for path in layer.paths]
        simplified = _cgal_simplify(polylines, threshold)

        for path, pts_simplified in zip(layer.paths, simplified):
            path.points = [Point(pt[0], pt[1], pt[2]) for pt in pts_simplified]
            remaining_pts_num += len(path.points)

    logger.info(f'{remaining_pts_num} points remaining after simplification')


def _simplify_paths_python(slicer: BaseSlicer, threshold: float) -> None:
    """Simplify paths using Python rdp library."""
    logger.info("Paths simplification rdp (Python)")
    remaining_pts_num = 0

    for layer in slicer.layers:
        if layer.is_raft:
            continue

        for path in layer.paths:
            pts_rdp = rdp_py.rdp(np.array(path.points), epsilon=threshold)
            path.points = [Point(pt[0], pt[1], pt[2]) for pt in pts_rdp]
            remaining_pts_num += len(path.points)

    logger.info(f'{remaining_pts_num} points remaining after simplification')


if __name__ == "__main__":
    pass
