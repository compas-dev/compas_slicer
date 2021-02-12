import logging
import math

import compas_slicer
from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path

from compas.geometry import Point
from compas.geometry import Line
from compas.geometry import Vector
from compas.geometry import bounding_box_xy
from compas.geometry import offset_polygon
from compas.geometry import intersection_line_line
from compas.geometry import offset_line

logger = logging.getLogger('logger')

__all__ = ['generate_raft']


def generate_raft(slicer,
                  raft_offset=10,
                  distance_between_paths=10,
                  direction="xy_diagonal",
                  raft_layers=1,
                  raft_layer_height=None):
    """Creates a raft.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers.BaseSlicer classes.
    raft_offset: float
        Distance (in mm) that the raft should be offsetted from the first layer. Defaults to 10mm
    distance_between_paths: float
        Distance (in mm) between the printed lines of the raft. Defaults to 10mm
    direction: str
        x_axis: Create a raft aligned with the x_axis
        y_axis: Create a raft aligned with the y_axis
        xy_diagonal: Create a raft int the diagonal direction in the xy_plane
    raft_layers: int
        Number of raft layers to add. Defaults to 1
    raft_layer_height: float
        Layer height of the raft layers. Defaults to same value as used in the slicer.
    """

    # check if a raft_layer_height is specified, if not, use the slicer.layer_height value
    if not raft_layer_height:
        raft_layer_height = slicer.layer_height

    logger.info("Generating raft")

    # find if slicer has vertical or horizontal layers, and select which paths are to be offset.
    if isinstance(slicer.layers[0], compas_slicer.geometry.VerticalLayer):  # Vertical layers
        # then find all paths that lie on the print platform and make them brim.
        paths_to_offset, _ = slicer.find_vertical_layers_with_first_path_on_base()

    else:  # Horizontal layers
        # then replace the first layer with a raft layer.
        paths_to_offset = slicer.layers[0].paths

    # get flat lists of points in bottom layer
    all_pts = []
    for path in paths_to_offset:
        for pt in path.points:
            all_pts.append(pt)

    # get xy bounding box of bottom layer and create offset
    bb_xy = bounding_box_xy(all_pts)
    bb_xy_offset = offset_polygon(bb_xy, -raft_offset)
    # bring points in the xy_offset to the correct height
    for pt in bb_xy_offset:
        pt[2] = slicer.layers[0].paths[0].points[0][2]

    # calculate x range, y range, and number of steps
    x_range = abs(bb_xy_offset[0][0] - bb_xy_offset[1][0])
    y_range = abs(bb_xy_offset[0][1] - bb_xy_offset[3][1])

    # get maximum values of the bounding box
    bb_max_x_right = bb_xy_offset[1][0]
    bb_max_y_top = bb_xy_offset[3][1]

    # get point in bottom left corner as raft start point
    raft_start_pt = Point(bb_xy_offset[0][0], bb_xy_offset[0][1], bb_xy_offset[0][2])

    # create starting line for diagonal direction
    if direction == "xy_diagonal":
        c = math.sqrt(2*(distance_between_paths**2))

        pt1 = Point(raft_start_pt[0] + c, raft_start_pt[1], raft_start_pt[2])
        pt2 = Point(pt1[0] - y_range, pt1[1] + y_range, pt1[2])
        line = Line(pt1, pt2)

    # move all points in the slicer up so that raft layers can be inserted
    for i, layer in enumerate(slicer.layers):
        for j, path in enumerate(layer.paths):
            for k, pt in enumerate(path.points):
                slicer.layers[i].paths[j].points[k] = Point(pt[0], pt[1], pt[2] + (raft_layers)*raft_layer_height)

    for i in range(raft_layers):

        iter = 0
        raft_points = []

        # create raft points depending on the chosen direction
        while iter < 9999:  # to avoid infinite while loop in case something is not correct
            # ===============
            # VERTICAL RAFT
            # ===============
            if direction == "y_axis":
                raft_pt1 = Point(raft_start_pt[0] + iter*distance_between_paths, raft_start_pt[1], raft_start_pt[2] + i*raft_layer_height)
                raft_pt2 = Point(raft_start_pt[0] + iter*distance_between_paths, raft_start_pt[1] + y_range, raft_start_pt[2] + i*raft_layer_height)

                if raft_pt2[0] > bb_max_x_right or raft_pt1[0] > bb_max_x_right:
                    break

            # ===============
            # HORIZONTAL RAFT
            # ===============
            elif direction == "x_axis":
                raft_pt1 = Point(raft_start_pt[0], raft_start_pt[1] + iter*distance_between_paths, raft_start_pt[2] + i*raft_layer_height)
                raft_pt2 = Point(raft_start_pt[0] + x_range, raft_start_pt[1] + iter*distance_between_paths, raft_start_pt[2] + i*raft_layer_height)

                if raft_pt2[1] > bb_max_y_top or raft_pt1[1] > bb_max_y_top:
                    break

            # ===============
            # DIAGONAL RAFT
            # ===============
            elif direction == "xy_diagonal":
                # create offset of the initial diagonal line
                offset_l = offset_line(line, iter*distance_between_paths, Vector(0, 0, -1))

                # get intersections for the initial diagonal line with the left and bottom of the bb
                int_left = intersection_line_line(offset_l, [bb_xy_offset[0], bb_xy_offset[3]])
                int_bottom = intersection_line_line(offset_l, [bb_xy_offset[0], bb_xy_offset[1]])

                # get the points at the intersections
                raft_pt1 = Point(int_left[0][0], int_left[0][1], int_left[0][2] + i*raft_layer_height)
                raft_pt2 = Point(int_bottom[0][0], int_bottom[0][1], int_bottom[0][2] + i*raft_layer_height)

                # if the intersection goes beyond the height of the left side of the bounding box:
                if int_left[0][1] > bb_max_y_top:
                    # create intersection with the top side
                    int_top = intersection_line_line(offset_l, [bb_xy_offset[3], bb_xy_offset[2]])
                    raft_pt1 = Point(int_top[0][0], int_top[0][1], int_top[0][2] + i*raft_layer_height)

                    # if intersection goes beyond the length of the top side, break
                    if raft_pt1[0] > bb_max_x_right:
                        break

                # if the intersection goes beyond the length of the bottom side of the bounding box:
                if int_bottom[0][0] > bb_max_x_right:
                    # create intersection with the right side
                    int_right = intersection_line_line(offset_l, [bb_xy_offset[1], bb_xy_offset[2]])
                    raft_pt2 = Point(int_right[0][0], int_right[0][1], int_right[0][2] + i*raft_layer_height)

                    # if intersection goes beyond the height of the right side, break
                    if raft_pt2[1] > bb_xy_offset[2][1]:
                        break

            # append to list alternating
            if iter % 2 == 0:
                raft_points.extend((raft_pt1, raft_pt2))
            else:
                raft_points.extend((raft_pt2, raft_pt1))

            iter += 1

        # create raft layer
        raft_layer = Layer([Path(raft_points, is_closed=False)])
        raft_layer.is_raft = True
        # insert raft layer in the correct position into the slicer
        slicer.layers.insert(i, raft_layer)


if __name__ == "__main__":
    pass
