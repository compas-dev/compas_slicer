import rdp as rdp
import numpy as np
import logging

from compas.geometry import Point
# from compas_slicer.geometry import PrintPoint, Contour

logger = logging.getLogger('logger')

__all__ = ['simplify_paths_rdp']


def simplify_paths_rdp(slicer, threshold):
    """Simplifies a path using the Ramer–Douglas–Peucker algorithm.
    https://en.wikipedia.org/wiki/Ramer-Douglas-Peucker_algorithm

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    threshold: float
        Controls the degree of polyline simplification.
        Low threshold removes few points, high threshold removes many points.

    """

    logger.info("Paths simplification rdp")
    remaining_pts_num = 0
    for layer in slicer.layers:
        for path in layer.paths:
            pts_rdp = rdp.rdp(np.array(path.points), epsilon=threshold)
            path.points = [Point(pt[0], pt[1], pt[2]) for pt in pts_rdp]
            remaining_pts_num += len(path.points)
    logger.info('%d Points remaining after rdp simplification' % remaining_pts_num)
