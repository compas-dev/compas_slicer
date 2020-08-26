import rdp
import numpy as np
import logging
from rdp import rdp

from compas.geometry import Point
from compas_slicer.geometry import AdvancedPrintPoint, Contour

logger = logging.getLogger('logger')

__all__ = ['simplify_paths_rdp']


def simplify_paths_rdp(slicer, threshold):

    # TODO: simplify_path_rdp() is slow and should be optimized.

    logger.info("Paths simplification rdp")
    for layer in slicer.print_paths:
        contours_new = []
        for contour in layer.contours:
            contour_new = simplify_path_rdp(contour, threshold)
            contours_new.append(contour_new)
        layer.contours = contours_new


def simplify_path_rdp(path, threshold):
    initial_points_number = len(path.printpoints)
    pts = path.printpoints
    pts_rdp = rdp(np.array(pts), epsilon=threshold)

    # recreate points as compas.geometry.Point
    points_per_contour = []
    for pt in pts_rdp:
        new_pt = Point(pt[0], pt[1], pt[2])
        points_per_contour.append(new_pt)
    
    # recrate path as compas_slicer.geometry.path.Contour
    path = Contour(points=points_per_contour, is_closed=True)
    
    logger.debug("Path simplification rdp: %d printpoints removed" % (initial_points_number - len(path.printpoints)))
    return path