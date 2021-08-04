import logging

from compas.geometry import Point
from compas.geometry import distance_point_point

logger = logging.getLogger('logger')

__all__ = ['seams_align']


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
