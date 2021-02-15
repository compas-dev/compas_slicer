import compas
import compas_slicer
from compas.geometry import closest_point_on_polyline, distance_point_point, Polyline, Vector, normalize_vector, Point
import logging
from compas_slicer.geometry import Path, PrintPoint
import compas_slicer.utilities as utils
import progressbar
from compas_slicer.parameters import get_param

logger = logging.getLogger('logger')
__all__ = ['VerticalConnectivity']


class VerticalConnectivity:
    """
    VerticalConnectivity finds the vertical relation between paths in a segment.
    It assumes that each path is supported by the path below, and the first path is
    supported by the BaseBoundary.
    This class creates PrintPoints and fills in their information.

    Attributes
    ----------
    paths : list of instances of compas_slicer.geometry.Path
    base_boundary : compas_slicer.print_organization.BaseBoundary
    mesh : compas.geometry.Mesh
    parameters : dict
    """

    def __init__(self, paths, base_boundary, mesh, parameters):
        assert isinstance(paths[0], compas_slicer.geometry.Path)
        assert isinstance(base_boundary, compas_slicer.print_organization.BaseBoundary)
        assert isinstance(mesh, compas.datastructures.Mesh)

        self.paths = paths
        self.base_boundary = base_boundary
        self.mesh = mesh
        self.parameters = parameters
        self.printpoints = {}  # dict with pne list of printpoints per path



if __name__ == "__main__":
    pass
