import math
from compas.geometry import distance_point_line_sqrd, distance_point_point_sqrd

__all__ = ['curvature_subsampling']

def curvature_subsampling(points, threshold, iterations):
    """
    Simplifies the polyline by only removing points that lie on the linear segments, whose removal does not affect significantly the shape of the polyline
    
    Attributes
    ----------
    points : list
        compas.geometry.Point
    threshold : float
        The lower the threshold, the more points are removed
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
                prev_pt = points[prev_index].pt
                next_pt = points[next_index].pt
                d_inner_sqrd = distance_point_line_sqrd(point=point.pt, line=[prev_pt, next_pt])
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
