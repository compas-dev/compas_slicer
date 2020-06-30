import math
from compas.geometry import distance_point_line_sqrd, distance_point_point_sqrd
import logging

logger = logging.getLogger('logger')

__all__ = ['simplify_paths_curvature']


def simplify_paths_curvature(slicer, threshold, iterations=2):
    logger.info("Paths simplification curvature")
    threshold = 3.3 / threshold  # Trying to make the same threshold have the same meaning for all simplification methods. Here as threshold goes down more printpoints are removed, thus k/threshold to avoid confusion
    for printpath_group in slicer.print_paths:
        [simplify_path_curvature(path, threshold, iterations) for path in printpath_group.get_all_paths()]


def simplify_path_curvature(path, threshold,  iterations):
    initial_points_number = len(path.printpoints)
    path_points = [p.pt for p in path.printpoints]
    reduced_pts = simplify_points(path_points, threshold,  iterations)
    path.printpoints = [point for point in path.printpoints if point.pt in reduced_pts]
    logger.debug("Path simplification curvature: %d printpoints removed" % (initial_points_number - len(path.printpoints)))


def simplify_points(points, threshold, iterations):
    """
    Simplifies the polyline by only removing printpoints that lie on the linear segments, whose removal does not affect significantly the shape of the polyline
    
    Attributes
    ----------
    points : list
        compas.geometry.Point
    threshold : float
        The lower the threshold, the more printpoints are removed
    iterations : int
        How many iterations to perform. 2 is a good number. 
    """

    threshold = threshold * 10

    for j in range(iterations):
        indices_to_remove = []
        points_to_remove = []

        for i, point in enumerate(points):
            prev_index = find_prev_index(i, indices_to_remove)
            next_index = find_next_index(i, indices_to_remove, len(points))

            if prev_index and next_index:
                prev_pt = points[prev_index]
                next_pt = points[next_index]
                d_inner_sqrd = distance_point_line_sqrd(point=point, line=[prev_pt, next_pt])
                d_outer_sqrd = distance_point_point_sqrd(prev_pt, next_pt)
                if d_inner_sqrd > 0:
                    if math.sqrt(d_outer_sqrd / d_inner_sqrd) > threshold:
                        indices_to_remove.append(i)
                        points_to_remove.append(points[i])
                else:
                    indices_to_remove.append(i)
                    points_to_remove.append(points[i])

        for point in points_to_remove:
            points.remove(point)

    return points


def find_prev_index(i, indices_to_remove):
    """ Find index that has not been labeled as 'to be removed' """
    count = 1
    while count < 10 and i - count >= - 2:
        prev_index = i - count
        if prev_index in indices_to_remove:
            count += 1
        else:
            return prev_index


def find_next_index(i, indices_to_remove, max_num):
    """ Find index that has not been labeled as 'to be removed' """
    count = 1
    while count < 10 and i + count < max_num + 2:
        next_index = (i + count) % max_num
        if next_index in indices_to_remove:
            count += 1
        else:
            return next_index


if __name__ == "__main__":
    pass
