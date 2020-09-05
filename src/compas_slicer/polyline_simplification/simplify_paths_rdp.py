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
    for path_collection in slicer.path_collections:
        for path in path_collection.paths:
            initial_points_number = len(path.points)
            pts_rdp = rdp(np.array(path.points), epsilon=threshold)
            path.points = [Point(pt[0], pt[1], pt[2]) for pt in pts_rdp]
            logger.debug("Contour simplification rdp: %d printpoints removed" % (initial_points_number - len(path.points)))
