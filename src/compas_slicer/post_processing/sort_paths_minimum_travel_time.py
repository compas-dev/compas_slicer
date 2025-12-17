from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from compas.geometry import Point
from loguru import logger

if TYPE_CHECKING:
    from compas_slicer.geometry import Path as SlicerPath
    from compas_slicer.slicers import BaseSlicer


__all__ = ["sort_paths_minimum_travel_time"]


def sort_paths_minimum_travel_time(slicer: BaseSlicer) -> None:
    """Sorts the paths within a horizontal layer to reduce total travel time.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    """
    logger.info("Sorting contours to minimize travel time")

    ref_point = Point(2**32, 0, 0)  # set the reference point to the X-axis

    for i, layer in enumerate(slicer.layers):
        sorted_paths = []
        while len(layer.paths) > 0:
            index = closest_path(ref_point, layer.paths)  # find the closest path to the reference point
            sorted_paths.append(layer.paths[index])  # add the closest path to the sorted list
            ref_point = layer.paths[index].points[-1]
            layer.paths.pop(index)

        slicer.layers[i].paths = sorted_paths


def adjust_seam_to_closest_pos(ref_point: Point, path: SlicerPath) -> None:
    """Aligns the seam (start- and endpoint) of a contour so that it is closest to a given point.
    for open paths, check if the end point closest to the reference point is the start point

    Parameters
    ----------
    ref_point: :class:`compas.geometry.Point`
        The reference point
    path: :class:`compas_slicer.geometry.Path`
        The contour to be adjusted.
    """

    # TODO: flip orientation to reduce angular velocity

    if path.is_closed:  # if path is closed
        # remove first point
        path.points.pop(-1)
        #  calculate distances from ref_point to vertices of path (vectorized)
        ref = np.asarray(ref_point, dtype=np.float64)
        pts = np.asarray(path.points, dtype=np.float64)
        distances = np.linalg.norm(pts - ref, axis=1)
        closest_point = int(np.argmin(distances))
        #  adjust seam
        adjusted_seam = path.points[closest_point:] + path.points[:closest_point] + [path.points[closest_point]]
        path.points = adjusted_seam
    else:  # if path is open
        #  if end point is closer than start point >> flip (vectorized)
        ref = np.asarray(ref_point, dtype=np.float64)
        d_start = np.linalg.norm(np.asarray(path.points[0]) - ref)
        d_end = np.linalg.norm(np.asarray(path.points[-1]) - ref)
        if d_start > d_end:
            path.points.reverse()


def closest_path(ref_point: Point, somepaths: list[SlicerPath]) -> int:
    """Finds the closest path to a reference point in a list of paths.

    Parameters
    ----------
    ref_point: the reference point
    somepaths: list of paths to look into for finding the closest
    """
    ref = np.asarray(ref_point, dtype=np.float64)

    # First adjust all seams
    for path in somepaths:
        adjust_seam_to_closest_pos(ref_point, path)

    # Then find closest path (vectorized)
    start_pts = np.array([path.points[0] for path in somepaths], dtype=np.float64)
    distances = np.linalg.norm(start_pts - ref, axis=1)
    return int(np.argmin(distances))


if __name__ == "__main__":
    pass
