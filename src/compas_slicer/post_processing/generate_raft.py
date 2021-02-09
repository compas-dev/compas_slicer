import logging

import compas_slicer
from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path

from compas.geometry import Point
from compas.geometry import bounding_box_xy
from compas.geometry import offset_polygon

logger = logging.getLogger('logger')

__all__ = ['generate_raft']


def generate_raft(slicer,
                  raft_offset=10,
                  distance_between_paths=10,
                  direction="x_axis",
                  raft_layers=1,
                  raft_layer_height="default"):
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
        x_axis: Aligns the raft with the x axis
        y_axis: Aligns the raft with the y_axis
    raft_layers: int
        Number of raft layers to add. Defaults to 1
    raft_layer_height: float
        Layer height of the raft layers. Defaults to same value as used in the slicer.
    """

    # check if a raft_layer_height is specified, if not, use the slicer.layer_height value
    if raft_layer_height == "default":
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

    # calculate x range, y range, and number of steps
    x_range = abs(bb_xy_offset[0][0] - bb_xy_offset[1][0])
    y_range = abs(bb_xy_offset[0][1] - bb_xy_offset[3][1])
    if direction == "y_axis":
        no_of_steps = int(x_range/distance_between_paths)
    elif direction == "x_axis":
        no_of_steps = int(y_range/distance_between_paths)

    # get raft start point with correct z height
    raft_start_pt = Point(bb_xy_offset[0][0], bb_xy_offset[0][1], slicer.layers[0].paths[0].points[0][2])

    # move all points in the slicer up so that raft layers can be inserted
    for i, layer in enumerate(slicer.layers):
        for j, path in enumerate(layer.paths):
            for k, pt in enumerate(path.points):
                slicer.layers[i].paths[j].points[k] = Point(pt[0], pt[1], pt[2] + (raft_layers-1)*raft_layer_height)

    for i in range(raft_layers):
        raft_points = []

        for j in range(no_of_steps+1):
            # create raft points depending on the chosen direction
            if direction == "y_axis":
                raft_pt1 = Point(raft_start_pt[0] + j*distance_between_paths, raft_start_pt[1], raft_start_pt[2] + i*raft_layer_height)
                raft_pt2 = Point(raft_start_pt[0] + j*distance_between_paths, raft_start_pt[1] + y_range, raft_start_pt[2] + i*raft_layer_height)
            elif direction == "x_axis":
                raft_pt1 = Point(raft_start_pt[0], raft_start_pt[1] + j*distance_between_paths, raft_start_pt[2] + i*raft_layer_height)
                raft_pt2 = Point(raft_start_pt[0] + x_range, raft_start_pt[1] + j*distance_between_paths, raft_start_pt[2] + i*raft_layer_height)

            # append to list alternating
            if j % 2 == 0:
                raft_points.extend((raft_pt1, raft_pt2))
            else:
                raft_points.extend((raft_pt2, raft_pt1))

        # create raft layer
        raft_layer = Layer([Path(raft_points, is_closed=False)])
        # insert raft layer in the correct position into the slicer
        slicer.layers.insert(i, raft_layer)

if __name__ == "__main__":
    pass
