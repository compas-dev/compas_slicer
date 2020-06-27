import rdp
import numpy as np
import logging
from rdp import rdp

logger = logging.getLogger('logger')

__all__ = ['simplify_paths_rdp']


def simplify_paths_rdp(slicer, threshold):
    logger.info("Paths simplification rdp")
    for printpath_group in slicer.print_paths:
        [simplify_path_rdp(path, threshold) for path in printpath_group.get_all_paths()]


def simplify_path_rdp(path, threshold):
    initial_points_number = len(path.points)
    path_points = [p.pt for p in path.points]
    reduced_pts = rdp(np.array(path_points), epsilon=threshold)
    path.points = [point for point in path.points if point.pt in reduced_pts]
    logger.debug("Path simplification rdp: %d points removed" % (initial_points_number - len(path.points)))
