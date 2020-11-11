import numpy as np
import logging
import compas_slicer.utilities as utils
from compas.plugins import PluginNotInstalledError
from compas_slicer.pre_processing.curved_slicing_preprocessing.gradient import get_scalar_field_from_gradient, \
    get_face_gradient_from_scalar_field, normalize_gradient
import scipy

packages = utils.TerminalCommand('conda list').get_split_output_strings()
if 'igl' in packages:
    import igl

logger = logging.getLogger('logger')

__all__ = ['get_igl_EXACT_geodesic_distances',
           'get_custom_HEAT_geodesic_distances']


def get_igl_EXACT_geodesic_distances(mesh, vertices_start):
    """
    Calculate geodesic distances using libigl.

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    vertices_start: list, int
    """

    if 'igl' not in packages:
        raise PluginNotInstalledError("--------ATTENTION! ----------- \
                        Libigl library is missing! \
                        Install it with 'conda install -c conda-forge igl'")
    v, f = mesh.to_vertices_and_faces()
    v = np.array(v)
    f = np.array(f)
    vertices_target = np.arange(len(v))  # all vertices are targets
    vstart = np.array(vertices_start)
    distances = igl.exact_geodesic(v, f, vstart, vertices_target)
    return distances


def get_custom_HEAT_geodesic_distances(mesh, vi_sources, OUTPUT_PATH,
                                       anisotropic_scaling, equalized_v_indices=None):
    """ Calculate geodesic distances using the heat method. """

    geodesics_solver = GeodesicsSolver(mesh, OUTPUT_PATH)
    u = geodesics_solver.diffuse_heat(vi_sources)
    geodesic_dist = geodesics_solver.get_geodesic_distances(u)
    return geodesic_dist


######################################
# --- GeodesicsSolver

class GeodesicsSolver:
    """ Computes custom geodesic distances. """

    def __init__(self, mesh, OUTPUT_PATH):
        logger.info('GeodesicsSolver')
        self.mesh = mesh
        self.OUTPUT_PATH = OUTPUT_PATH

        v, f = mesh.to_vertices_and_faces()
        v = np.array(v)
        f = np.array(f)

        ## compute necessary data
        self.cotans = igl.cotmatrix_entries(v, f)  # compute_cotan_field(self.mesh)
        self.L = igl.cotmatrix(v, f)  # assemble_laplacian_matrix(self.mesh, self.cotans)
        self.M = igl.massmatrix(v, f)  # create_mass_matrix(mesh)

    def diffuse_heat(self, vi_sources, method='default'):
        """ Heat diffusion. """

        # First assign starting values (0 everywhere, 1 on the sources)
        u0 = np.zeros(len(list(self.mesh.vertices())))
        u0[vi_sources] = 1.0

        if method == 'default':
            t_mult = 1
            t = t_mult * np.mean(np.array([self.mesh.face_area(fkey) for fkey in self.mesh.faces()]))  # avg face area
            solver = scipy.sparse.linalg.factorized(self.M - t * self.L)  # pre-factor solver
            u = solver(u0)  # solve the heat equation: u = (VA - t * Lc) * u0
            utils.save_to_json([float(value) for value in u], self.OUTPUT_PATH, 'diffused_heat.json')
            return u

        else:
            raise NotImplementedError

    def get_geodesic_distances(self, u):
        X = get_face_gradient_from_scalar_field(self.mesh, u)
        X = normalize_gradient(X)
        geodesic_dist = get_scalar_field_from_gradient(self.mesh, X, self.L, self.cotans)
        return geodesic_dist


if __name__ == "__main__":
    pass
