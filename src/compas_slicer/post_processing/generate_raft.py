import logging
from compas.geometry._core import distance

import pyclipper
from pyclipper import scale_from_clipper, scale_to_clipper

import compas_slicer
from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path

from compas.geometry import Point
from compas.geometry import bounding_box_xy
from compas.geometry import offset_polygon

from compas_slicer.post_processing import seams_align

logger = logging.getLogger('logger')

__all__ = ['generate_raft']


def generate_raft(slicer, raft_offset=10, distance_between_lines=10, direction="x_axis"):
    """Creates a raft.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers.BaseSlicer classes.
    raft_offset: float
        Distance (in mm) that the raft should be offsetted from the first layer.
    distance_between_lines: float
        Distance (in mm) between the printed lines of the raft.
    direction: str
        x_axis: Aligns the raft with the x axis
        y_axis: Aligns the raft with the y_axis
    """

    logger.info("Generating raft")

    # find if slicer has vertical or horizontal layers, and select which paths are to be offset.
    if isinstance(slicer.layers[0], compas_slicer.geometry.VerticalLayer):  # Vertical layers
        # then find all paths that lie on the print platform and make them brim.
        paths_to_offset, _ = slicer.find_vertical_layers_with_first_path_on_base()
        has_vertical_layers = True

    else:  # Horizontal layers
        # then replace the first layer with a raft layer.
        paths_to_offset = slicer.layers[0].paths
        has_vertical_layers = False

    # get flat lists of points in bottom layer
    all_pts = []
    for path in paths_to_offset:
        for pt in path.points:
            all_pts.append(pt)

    # get xy bounding box and create offset
    bb_xy = bounding_box_xy(all_pts)
    bb_xy_offset = offset_polygon(bb_xy, -raft_offset)

    # calculate x range, y range and number of steps
    x_range = abs(bb_xy_offset[0][0] - bb_xy_offset[1][0])
    y_range = abs(bb_xy_offset[0][1] - bb_xy_offset[3][1])
    if direction == "y_axis":
        no_of_steps = int(x_range/distance_between_lines)
    elif direction == "x_axis":
        no_of_steps = int(y_range/distance_between_lines)

    # get raft start point
    raft_start_pt = bb_xy_offset[0]

    raft_points = []
    for i in range(no_of_steps+1):
        # create raft points depending on the chosen direction
        if direction == "y_axis":
            raft_pt1 = Point(raft_start_pt[0] + i*distance_between_lines, raft_start_pt[1], raft_start_pt[2])
            raft_pt2 = Point(raft_start_pt[0] + i*distance_between_lines, raft_start_pt[1] + y_range, raft_start_pt[2])
        elif direction == "x_axis":
            raft_pt1 = Point(raft_start_pt[0], raft_start_pt[1] + i*distance_between_lines, raft_start_pt[2])
            raft_pt2 = Point(raft_start_pt[0] + x_range, raft_start_pt[1] + i*distance_between_lines, raft_start_pt[2])
        # append to list alternating
        if i % 2 == 0:
            raft_points.extend((raft_pt1, raft_pt2))
        else:
            raft_points.extend((raft_pt2, raft_pt1))

    # create raft layer
    raft_layer = Layer([Path(raft_points, is_closed=False)])

    # add the raft layer to the slicer
    if not has_vertical_layers:
        slicer.layers[0] = raft_layer  # replace first layer
    else:
        slicer.layers.insert(0, raft_layer)  # insert brim layer as the first layer of the slicer


if __name__ == "__main__":
    pass
