# from compas_slicer.geometry import VerticalLayersManager
import logging
from compas.geometry import Point
from compas.geometry import distance_point_point

logger = logging.getLogger('logger')

__all__ = ['sort_paths']  # ???


def sort_paths(slicer):
    """Sorts the paths for an optimised toolpath, minimising total travel distances.

      Parameters
    ----------
   some_layers: layers to sort
         Returns
    ----------
    layers with sorted contours
    """
    logger.info("Sorting contours ...")

    this_point = Point(0, 0, 0)  # set the reference point to the origin

    for i, layer in enumerate(slicer.layers):
        sorted_paths = []
        while len(layer.paths) > 0:
            index = closest_path(this_point, layer.paths)  # find the closest path to the reference point
            sorted_paths.append(layer.paths[index])  # add the closest path to the sorted list
            del layer.paths[index]  # delete the added path from the layer
            this_point = layer.paths[index].points[-1]

        slicer.layers[i].paths = sorted_paths


def adjust_seam_to_closest_pos(this_point, a_path):
    """Aligns the seam (start- and endpoint) of a contour so that it is closest to a given point.
    for open paths, check if the end point closest to the reference point is the start point

    Parameters
    ----------
    thispoint: the reference point
    apath: the contour to be adjusted
        layer.path

    TODO: flip orientation to reduce angular velocity

    Returns
    -------
    """

    if a_path.is_closed:  # if path is closed
        #  calculate distances from this_point to vertices of a_path
        distances = [distance_point_point(this_point, points) for points in a_path]
        #  find  index of closest point
        closest_point = distances.index(min(distances))
        #  adjust seam
        adjusted_seam = a_path[closest_point:] + a_path[:closest_point]
        a_path.points = adjusted_seam
    else:  # if path is open
        #  if end point is closer than start point >> flip
        if distance_point_point(this_point, a_path[0]) > distance_point_point(this_point, a_path[-1]):
            a_path.reverse()


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
    closest_index = 0

    for i, path in enumerate(somepaths.paths):
        #  for each path, adjust the seam to be in the closest vertex to this_point
        adjust_seam_to_closest_pos(thispoint, path)
        #  calculate the minimum distance to the nearest seam of each path
        min_dist_temp = distance_point_point(thispoint, path.points[0])
        if min_dist_temp < min_dist:
            min_dist = min_dist_temp
            closest_index = i
    return closest_index


if __name__ == "__main__":
    pass
