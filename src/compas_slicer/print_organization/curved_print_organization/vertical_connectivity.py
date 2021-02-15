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

    def __repr__(self):
        return "<VerticalConnectivity with %i paths>" % len(self.paths)

    ######################
    # Main
    def compute(self):
        """ Run the segment connectivity process. """
        self.initialize_printpoints()
        self.fill_in_printpoints_information()

        h_smoothing = get_param(self.parameters, key='layer_heights_smoothing', defaults_type='print_organization')
        if h_smoothing[0]:
            logger.info('Layer heights smoothing using horizontal neighbors')
            self.smooth_printpoints_layer_heights(iterations=h_smoothing[1], strength=h_smoothing[2])
        v_smoothing = get_param(self.parameters, key='up_vectors_smoothing', defaults_type='print_organization')
        if v_smoothing[0]:
            logger.info('Up vectors smoothing using horizontal neighbors')
            self.smooth_up_vectors(iterations=v_smoothing[1], strength=v_smoothing[2])

    ######################
    # Utilities
    def initialize_printpoints(self):
        """ Initializes printpoints in a list, without filling in their attributes. """

        all_pts = [pt for path in self.paths for pt in path.points]
        closest_fks, projected_pts = utils.pull_pts_to_mesh_faces(self.mesh, all_pts)
        normals = [Vector(*self.mesh.face_normal(fkey)) for fkey in closest_fks]

        count = 0
        for i, path in enumerate(self.paths):
            self.printpoints[i] = []
            for pt in path.points:
                self.printpoints[i].append(PrintPoint(pt=pt, layer_height=None, mesh_normal=normals[count]))
                count += 1

    def fill_in_printpoints_information(self):
        """ Fills in the attributes of previously initialized printpoints. """
        max_layer_height = get_param(self.parameters, key='max_layer_height', defaults_type='layers')
        min_layer_height = get_param(self.parameters, key='min_layer_height', defaults_type='layers')

        crv_to_check = Path(self.base_boundary.points, True)  # creation of fake path for the lower boundary
        with progressbar.ProgressBar(max_value=len(self.paths)) as bar:
            for i, path in enumerate(self.paths):
                for j, p in enumerate(path.points):
                    cp = closest_point_on_polyline(p, Polyline(crv_to_check.points))
                    d = distance_point_point(cp, p)

                    self.printpoints[i][j].closest_support_pt = Point(*cp)
                    self.printpoints[i][j].distance_to_support = d
                    self.printpoints[i][j].layer_height = max(min(d, max_layer_height), min_layer_height)
                    self.printpoints[i][j].up_vector = Vector(*normalize_vector(Vector.from_start_end(cp, p)))
                    self.printpoints[i][j].frame = self.printpoints[i][j].get_frame()

                bar.update(i)
                crv_to_check = path

    def smooth_printpoints_layer_heights(self, iterations, strength):
        """ Smooth printpoints heights based on neighboring. """
        for i, path in enumerate(self.paths):
            self.smooth_path_printpoint_attribute(i, iterations, strength, get_attr_value=lambda pp: pp.layer_height,
                                                  set_attr_value=set_printpoint_height)

    def smooth_up_vectors(self, iterations, strength):  # TODO: ATTENTION TO THE ATTRIBUTES THAT NEED TO BE RECOMPUTED
        """ Smooth printpoints up_vectors based on neighboring. """
        for i, path in enumerate(self.paths):
            self.smooth_path_printpoint_attribute(i, iterations, strength, get_attr_value=lambda pp: pp.up_vector,
                                                  set_attr_value=set_printpoint_up_vec)
            for pp in self.printpoints[i]:  # recompute frames
                pp.frame = pp.get_frame()

    def smooth_path_printpoint_attribute(self, path_index, iterations, strength, get_attr_value, set_attr_value):

        """General description.
        Parameters
        ----------
        path_index: int
        iterations: int
        strength: float
        get_attr_value: function that returns an attribute of a printpoint, get_attr_value(pp)
        set_attr_value: function that sets an attribute of a printpoint, set_attr_value(pp, new_value)
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
    """ Set printpoint.up_vector = v. """
    pp.up_vector = v


def set_printpoint_height(pp, h):
    """ Set printpoint.layer_height = h. """
    pp.layer_height = h


if __name__ == "__main__":
    pass
