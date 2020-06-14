import numpy as np
import logging

logger = logging.getLogger('logger')

__all__ = ['get_average_point_numpy']


def get_average_point_numpy(points):
    all_pts = np.array([point.pt for point in points])
    return np.mean(all_pts, axis=0)


if __name__ == "__main__":
    pass
