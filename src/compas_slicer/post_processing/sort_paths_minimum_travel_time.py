# from compas_slicer.geometry import VerticalLayersManager
import logging
from compas.geometry import Point
from compas.geometry import distance_point_point

logger = logging.getLogger('logger')

__all__ = ['sort_paths_minimum_travel_time']


def sort_paths_minimum_travel_time(slicer):
    """Sorts the paths within a horizontal layer to reduce total travel time.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    """
    logger.info("Sorting contours to minimize travel time")

    ref_point = Point(2 ** 32, 0, 0)  # set the reference point to the X-axis

    for i, layer in enumerate(slicer.layers):
        sorted_paths = []
        while len(layer.paths) > 0:
            index = closest_path(ref_point, layer.paths)  # find the closest path to the reference point
            sorted_paths.append(layer.paths[index])  # add the closest path to the sorted list
            ref_point = layer.paths[index].points[-1]
            layer.paths.pop(index)

        slicer.layers[i].paths = sorted_paths


def adjust_seam_to_closest_pos(ref_point, path):
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
        #  calculate distances from ref_point to vertices of path
        distances = [distance_point_point(ref_point, points) for points in path.points]
        #  find  index of closest point
        closest_point = distances.index(min(distances))
        #  adjust seam
        adjusted_seam = path.points[closest_point:] + path.points[:closest_point] + [path.points[closest_point]]
        path.points = adjusted_seam
    else:  # if path is open
        #  if end point is closer than start point >> flip
        if distance_point_point(ref_point, path.points[0]) > distance_point_point(ref_point, path.points[-1]):
            path.points.reverse()


def closest_path(ref_point, somepaths):
    """Finds the closest path to a reference point in a list of paths.

    Parameters
    ----------
    ref_point: the reference point
    somepaths: list of paths to look into for finding the closest
    """
    min_dist = distance_point_point(ref_point, somepaths[0].points[0])
    closest_index = 0

    for i, path in enumerate(somepaths):
        #  for each path, adjust the seam to be in the closest vertex to ref_point
        adjust_seam_to_closest_pos(ref_point, path)
        #  calculate the minimum distance to the nearest seam of each path
        min_dist_temp = distance_point_point(ref_point, path.points[0])
        if min_dist_temp < min_dist:
            min_dist = min_dist_temp
            closest_index = i
    return closest_index


if __name__ == "__main__":
    pass
