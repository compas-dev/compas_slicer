import logging

from compas.geometry import Point
from compas.geometry import distance_point_point

logger = logging.getLogger('logger')

__all__ = ['seams_align']


def closest_path(thispoint, somepaths):
    """Finds the closest path to a reference point in a list of paths.

    Parameters
    ----------
    thispoint: the reference point
    somepaths: list of paths to look into for finding the closest

    Returns
    -------
    """
    min_dist = distance_point_point(thispoint, somepaths.paths[0].points[0])
    min_index = 0

    for i, path in enumerate(somepaths.paths):
        adjust_seam_to_closest_pos(thispoint, path)
        min_dist_temp = distance_point_point(thispoint, path)
        if min_dist_temp < min_dist:
            min_dist = min_dist_temp
            min_index = i


    for i, layer in enumerate(slicer.layers):
        for j, path in enumerate(layer.paths):

            align_seams_for_current_path = path.is_closed  # should not happen if path is open

            if align_seams_for_current_path:
                #  get the points of the current layer and path
                path_to_change = layer.paths[j].points

                # check if start- and end-points are the same point
                if path_to_change[0] == path_to_change[-1]:
                    first_last_point_the_same = True
                    # if they are, remove the last point
                    path_to_change.pop(-1)
                else:
                    first_last_point_the_same = False

                if align_with == "next_path":
                    pt_to_align_with = None  # make sure aligning point is cleared

                    #  determines the correct point to align the current layer with
                    if len(layer.paths) == 1 and i == 0:
                        #  if ONE PATH and FIRST LAYER
                        #  >>> align with second layer
                        pt_to_align_with = slicer.layers[i + 1].paths[0].points[0]
                    if len(layer.paths) == 1 and i != 0:
                        #  if ONE PATH and NOT FIRST LAYER
                        #  >>> align with previous layer
                        pt_to_align_with = slicer.layers[i - 1].paths[0].points[0]
                    if len(layer.paths) != 1 and i == 0 and j == 0:
                        #  if MULTIPLE PATHS and FIRST LAYER and FIRST PATH
                        #  >>> align with second path of first layer
                        pt_to_align_with = slicer.layers[i].paths[i + 1].points[0]
                    if len(layer.paths) != 1 and j != 0:
                        #  if MULTIPLE PATHS and NOT FIRST PATH
                        #  >>> align with previous path
                        pt_to_align_with = slicer.layers[i].paths[j - 1].points[0]
                    if len(layer.paths) != 1 and i != 0 and j == 0:
                        #  if MULTIPLE PATHS and NOT FIRST LAYER and FIRST PATH
                        #  >>> align with first path of previous layer
                        pt_to_align_with = slicer.layers[i - 1].paths[j].points[0]

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

                #  computes distance between pt_to_align_with and the current path points
                distance_current_pt_align_pt = [distance_point_point(pt_to_align_with, pt) for pt in path_to_change]
                #  gets the index of the closest point by looking for the minimum
                new_start_index = distance_current_pt_align_pt.index(min(distance_current_pt_align_pt))
                #  shifts the list by the distance determined
                shift_list = path_to_change[new_start_index:] + path_to_change[:new_start_index]
                #  shifts the list by the distance determined
                # layer.paths[j].points = shift_list

                if first_last_point_the_same:
                    shift_list = shift_list + [shift_list[0]]

                layer.paths[j].points = shift_list


if __name__ == "__main__":
    pass
