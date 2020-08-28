import rdp
import numpy as np
import logging
from rdp import rdp

from compas.geometry import Point
from compas_slicer.geometry import AdvancedPrintPoint, Contour

logger = logging.getLogger('logger')

__all__ = ['simplify_paths_rdp']


def simplify_paths_rdp(slicer, threshold):

    logger.info("Paths simplification rdp")
    for layer in slicer.print_paths:
        for contour in layer.contours:
            initial_points_number = len(contour.points)
            pts_rdp = rdp(np.array(contour.points), epsilon=threshold)
            contour.points = [Point(pt[0], pt[1], pt[2]) for pt in pts_rdp]
            logger.debug("Contour simplification rdp: %d printpoints removed" % (initial_points_number - len(contour.points)))
