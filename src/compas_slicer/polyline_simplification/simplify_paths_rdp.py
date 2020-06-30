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
    path.points = rdp(np.array(path.points), epsilon=threshold)
    logger.debug("Path simplification rdp: %d printpoints removed" % (initial_points_number - len(path.points)))
