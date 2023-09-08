import rdp as rdp
import numpy as np
import logging
import progressbar
from compas.geometry import Point
import compas_slicer.utilities as utils
from compas.plugins import PluginNotInstalledError

packages = utils.TerminalCommand('conda list').get_split_output_strings()
if 'igl' in packages:
    import igl

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
        logger.info('%d Points remaining after rdp simplification' % remaining_pts_num)


def simplify_paths_rdp_igl(slicer, threshold):
    """
    https://libigl.github.io/libigl-python-bindings/igl_docs/#ramer_douglas_peucker
    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    threshold: float
        Controls the degree of polyline simplification.
        Low threshold removes few points, high threshold removes many points.
    """
    try:
        # utils.check_package_is_installed('igl')
        logger.info("Paths simplification rdp - igl")
        remaining_pts_num = 0

        for i, layer in enumerate(slicer.layers):
            if not layer.is_raft:  # no simplification necessary for raft layer
                for path in layer.paths:
                    pts = np.array([[pt[0], pt[1], pt[2]] for pt in path.points])
                    S, J, Q = igl.ramer_douglas_peucker(pts, threshold)
                    path.points = [Point(pt[0], pt[1], pt[2]) for pt in S]
                    remaining_pts_num += len(path.points)
        logger.info('%d Points remaining after rdp simplification' % remaining_pts_num)

    except PluginNotInstalledError:
        logger.info("Libigl is not installed. Falling back to python rdp function")
        simplify_paths_rdp(slicer, threshold)


if __name__ == "__main__":
    pass
