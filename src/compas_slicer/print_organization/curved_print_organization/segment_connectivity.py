import compas
import compas_slicer
from compas.geometry import closest_point_on_polyline, distance_point_point, Polyline, Vector, normalize_vector, Point
import logging
from compas_slicer.geometry import Path, PrintPoint
import compas_slicer.utilities as utils
import progressbar

logger = logging.getLogger('logger')
__all__ = ['SegmentConnectivity']


class SegmentConnectivity:
    """
    SegmentConnectivity finds the vertical relation between paths in a segment.
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

    def __repr__(self):
        return "<SegmentConnectivity with %i paths>" % len(self.paths)

    ######################
    # Main
    def compute(self):
        self.initialize_printpoints()
        self.fill_in_printpoints_information()

        if self.parameters['layer_heights_smoothing'][0]:
            logger.info('Layer heights smoothing using horizontal neighbors')
            self.smooth_printpoints_heights()
        if self.parameters['up_vectors_smoothing'][0]:
            logger.info('Up vectors smoothing using horizontal neighbors')
            self.smooth_up_vectors()

    ######################
    # Utilities
    def initialize_printpoints(self):
        for i, path in enumerate(self.paths):
            self.printpoints[i] = [PrintPoint(pt=p, layer_height=None,
                                              mesh_normal=utils.get_closest_mesh_normal(self.mesh, p))
                                   for p in path.points]

    def fill_in_printpoints_information(self):
        crv_to_check = Path(self.base_boundary.points, True)  # Fake path for the lower boundary
        with progressbar.ProgressBar(max_value=len(self.paths)) as bar:
            for i, path in enumerate(self.paths):
                for j, p in enumerate(path.points):
                    cp = closest_point_on_polyline(p, Polyline(crv_to_check.points))
                    d = distance_point_point(cp, p)

                    self.printpoints[i][j].closest_support_pt = Point(*cp)
                    self.printpoints[i][j].distance_to_support = d
                    self.printpoints[i][j].layer_height = max(min(d, self.parameters['max_layer_height']),
                                                            self.parameters['min_layer_height'])
                    self.printpoints[i][j].support_path = crv_to_check
                    self.printpoints[i][j].up_vector = Vector(*normalize_vector(Vector.from_start_end(cp, p)))
                    self.printpoints[i][j].frame = self.printpoints[i][j].get_frame()

                    if d < self.parameters['min_layer_height'] or d > self.parameters['max_layer_height']:
                        self.printpoints[i][j].is_feasible = False
                bar.update(i)
                crv_to_check = path

    def smooth_printpoints_heights(self):
        iterations = self.parameters['layer_heights_smoothing'][2]
        strength = self.parameters['layer_heights_smoothing'][3]
        for i, path in enumerate(self.paths):
            self.smooth_path_printpoint_attribute(i, iterations, strength, get_attr_value=lambda pp: pp.height,
                                                  set_attr_value=set_printpoint_height)

    def smooth_up_vectors(self):
        iterations = self.parameters['up_vectors_smoothing'][2]
        strength = self.parameters['up_vectors_smoothing'][3]
        for i, path in enumerate(self.paths):
            self.smooth_path_printpoint_attribute(i, iterations, strength, get_attr_value=lambda pp: pp.up_vector,
                                                  set_attr_value=set_printpoint_up_vec)

    def smooth_path_printpoint_attribute(self, path_index, iterations, strength, get_attr_value, set_attr_value):

        """General description.
        Parameters
        ----------
        param : type
            Explanation sentence.
        Returns
        -------
        what it returns
            Explanation sentence.

        :param path_index: int
        :param iterations: int
        :param strength: float
        :param get_attr_value: function that takes a printpoint, get_attr_value(pp)
        :param set_attr_value: function that takes a printpoint, set_attr_value(pp, new_value)
        :return: None
        """
        for _ in range(iterations):
            attributes = [get_attr_value(pp) for pp in self.printpoints[path_index]]

            if self.paths[path_index].is_closed:
                for j, v in enumerate(attributes):
                    mid = (attributes[j - 1] + attributes[(j + 1) % len(attributes)]) / 2
                    new_value = mid * strength + v * (1 - strength)
                    set_attr_value(self.printpoints[path_index][j], new_value)
            else:
                for j, v in enumerate(attributes):
                    if 0 < j < len(attributes) - 1:
                        mid = (attributes[j - 1] + attributes[(j + 1)]) / 2
                        new_value = mid * strength + v * (1 - strength)
                        set_attr_value(self.printpoints[path_index][j], new_value)


def set_printpoint_up_vec(pp, v):
    pp.up_vector = v


def set_printpoint_height(pp, h):
    pp.height = h
