import logging

import numpy as np
import progressbar
import rdp as rdp
from compas.geometry import Point
from compas.plugins import PluginNotInstalledError

logger = logging.getLogger('logger')

__all__ = ['simplify_paths_rdp',
           'simplify_paths_rdp_igl']


def simplify_paths_rdp(slicer, threshold):
    """Simplifies a path using the Ramer–Douglas–Peucker algorithm, implemented in the rdp python library.
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

    with progressbar.ProgressBar(max_value=len(slicer.layers)) as bar:
        for i, layer in enumerate(slicer.layers):
            if not layer.is_raft:  # no simplification necessary for raft layer
                for path in layer.paths:
                    pts_rdp = rdp.rdp(np.array(path.points), epsilon=threshold)
                    path.points = [Point(pt[0], pt[1], pt[2]) for pt in pts_rdp]
                    remaining_pts_num += len(path.points)
                    bar.update(i)
        logger.info(f'{remaining_pts_num} Points remaining after rdp simplification')


def simplify_paths_rdp_igl(slicer, threshold):
    """Simplify paths using Ramer-Douglas-Peucker from compas_libigl.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    threshold: float
        Controls the degree of polyline simplification.
        Low threshold removes few points, high threshold removes many points.
    """
    try:
        from compas_libigl.simplify import ramer_douglas_peucker

        logger.info("Paths simplification rdp - compas_libigl")
        remaining_pts_num = 0

        for _i, layer in enumerate(slicer.layers):
            if not layer.is_raft:  # no simplification necessary for raft layer
                for path in layer.paths:
                    pts = [[pt[0], pt[1], pt[2]] for pt in path.points]
                    S, _J, _Q = ramer_douglas_peucker(pts, threshold)
                    path.points = [Point(pt[0], pt[1], pt[2]) for pt in S]
                    remaining_pts_num += len(path.points)
        logger.info(f'{remaining_pts_num} Points remaining after rdp simplification')

    except (PluginNotInstalledError, ModuleNotFoundError):
        logger.info("compas_libigl is not installed. Falling back to python rdp function")
        simplify_paths_rdp(slicer, threshold)


if __name__ == "__main__":
    pass
