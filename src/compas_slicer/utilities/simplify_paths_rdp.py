import rdp
import numpy as np
import logging
from rdp import rdp

from compas.geometry import Point
# from compas_slicer.geometry import PrintPoint, Contour

logger = logging.getLogger('logger')

__all__ = ['simplify_paths_rdp']


def simplify_paths_rdp(slicer, threshold):

    logger.info("Paths simplification rdp")
    remaining_pts_num = 0
    for layer in slicer.layers:
        for path in layer.paths:
            pts_rdp = rdp(np.array(path.points), epsilon=threshold)
            path.points = [Point(pt[0], pt[1], pt[2]) for pt in pts_rdp]
            remaining_pts_num += len(path.points)
    logger.info('%d Points remaining after rdp simplification' % remaining_pts_num)
