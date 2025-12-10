from __future__ import annotations

from loguru import logger
from typing import TYPE_CHECKING, Literal

import numpy as np
from compas.geometry import Point

if TYPE_CHECKING:
    from compas_slicer.slicers import BaseSlicer


__all__ = ['seams_align']

AlignWith = Literal["next_path", "origin", "x_axis", "y_axis"]


def seams_align(slicer: BaseSlicer, align_with: AlignWith | Point = "next_path") -> None:
    """Aligns the seams (start- and endpoint) of a print.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    align_with: str or :class:`compas.geometry.Point`
        Direction to orient the seams in.
        next_path    = orients the seam to the next path
        origin       = orients the seam to the origin (0,0,0)
        x_axis       = orients the seam to the x_axis
        y_axis       = orients the seam to the y_axis
        Point(x,y,z) = orients the seam according to the given point

    """
    #  TODO: Implement random seams
    logger.info(f"Aligning seams to: {align_with}")

    for i, layer in enumerate(slicer.layers):
        for j, path in enumerate(layer.paths):

            if align_with == "next_path":
                pt_to_align_with = None  # make sure aligning point is cleared

                #  determines the correct point to align the current path with
                if len(layer.paths) == 1 and i == 0:
                    #  if ONE PATH and FIRST LAYER
                    #  >>> align with second layer
                    pt_to_align_with = slicer.layers[i + 1].paths[0].points[0]
                if len(layer.paths) == 1 and i != 0:
                    last_path_index = len(slicer.layers[i - 1].paths) - 1
                    #  if ONE PATH and NOT FIRST LAYER
                    #  >>> align with previous layer
                    pt_to_align_with = slicer.layers[i - 1].paths[last_path_index].points[-1]
                if len(layer.paths) != 1 and i == 0 and j == 0:
                    #  if MULTIPLE PATHS and FIRST LAYER and FIRST PATH
                    #  >>> align with second path of first layer
                    pt_to_align_with = slicer.layers[i].paths[i + 1].points[-1]
                if len(layer.paths) != 1 and j != 0:
                    #  if MULTIPLE PATHS and NOT FIRST PATH
                    #  >>> align with previous path
                    pt_to_align_with = slicer.layers[i].paths[j - 1].points[-1]
                if len(layer.paths) != 1 and i != 0 and j == 0:
                    #  if MULTIPLE PATHS and NOT FIRST LAYER and FIRST PATH
                    #  >>> align with first path of previous layer
                    last_path_index = len(slicer.layers[i - 1].paths) - 1
                    pt_to_align_with = slicer.layers[i - 1].paths[last_path_index].points[-1]

            elif align_with == "origin":
                pt_to_align_with = Point(0, 0, 0)
            elif align_with == "x_axis":
                pt_to_align_with = Point(2 ** 32, 0, 0)
            elif align_with == "y_axis":
                pt_to_align_with = Point(0, 2 ** 32, 0)
            elif isinstance(align_with, Point):
                pt_to_align_with = align_with
            else:
                raise NameError("Unknown align_with : " + str(align_with))

            # CLOSED PATHS
            if path.is_closed:
                #  get the points of the current layer and path
                path_to_change = layer.paths[j].points

                # check if start- and end-points are the same point
                if path_to_change[0] == path_to_change[-1]:
                    first_last_point_the_same = True
                    # if they are, remove the last point
                    path_to_change.pop(-1)
                else:
                    first_last_point_the_same = False

                #  computes distance between pt_to_align_with and the current path points (vectorized)
                ref = np.asarray(pt_to_align_with, dtype=np.float64)
                pts = np.asarray(path_to_change, dtype=np.float64)
                distances = np.linalg.norm(pts - ref, axis=1)
                #  gets the index of the closest point
                new_start_index = int(np.argmin(distances))
                #  shifts the list by the distance determined
                shift_list = path_to_change[new_start_index:] + path_to_change[:new_start_index]

                if first_last_point_the_same:
                    shift_list = shift_list + [shift_list[0]]

                layer.paths[j].points = shift_list

            else:
                # OPEN PATHS
                path_to_change = layer.paths[j].points

                # get the distance between the align point and the start/end point (vectorized)
                ref = np.asarray(pt_to_align_with, dtype=np.float64)
                d_start = np.linalg.norm(np.asarray(path_to_change[0]) - ref)
                d_end = np.linalg.norm(np.asarray(path_to_change[-1]) - ref)

                # if closer to end point > reverse list
                if d_start > d_end:
                    layer.paths[j].points.reverse()


if __name__ == "__main__":
    pass
