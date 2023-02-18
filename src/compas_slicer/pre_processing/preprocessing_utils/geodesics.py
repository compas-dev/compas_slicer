import numpy as np
import logging
import compas_slicer.utilities as utils
from compas_slicer.pre_processing.preprocessing_utils.gradient import get_scalar_field_from_gradient, \
    get_face_gradient_from_scalar_field, normalize_gradient
import scipy
import math

logger = logging.getLogger('logger')

__all__ = ['get_igl_EXACT_geodesic_distances',
           'get_custom_HEAT_geodesic_distances']


def get_igl_EXACT_geodesic_distances(mesh, vertices_start):
    """
    Calculate geodesic distances using libigl.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    vertices_start: list, int
    """
    # utils.check_package_is_installed('igl')
    import igl

    v, f = mesh.to_vertices_and_faces()
    v = np.array(v)
    f = np.array(f)
    vertices_target = np.arange(len(v))  # all vertices are targets
    vstart = np.array(vertices_start)
    distances = igl.exact_geodesic(v, f, vstart, vertices_target)
    return distances


def get_custom_HEAT_geodesic_distances(mesh, vi_sources, OUTPUT_PATH, v_equalize=None, anisotropic_scaling=False):
    """ Calculate geodesic distances using the heat method. """
    geodesics_solver = GeodesicsSolver(mesh, OUTPUT_PATH)
    u = geodesics_solver.diffuse_heat(vi_sources, v_equalize, method='simulation')
    geodesic_dist = geodesics_solver.get_geodesic_distances(u, vi_sources, v_equalize)
    return geodesic_dist


######################################
# --- GeodesicsSolver

USE_FORWARDS_EULER = False
HEAT_DIFFUSION_ITERATIONS = 250
DELTA = 0.1


class GeodesicsSolver:
    """
    Computes custom geodesic distances. Starts from implementation of the method presented in the paper
    'Geodesics in Heat' (Crane, 2013)

    Attributes
    ----------
    mesh: :class: compas.datastructures.Mesh
    OUTPUT_PATH: str
    """

    def __init__(self, mesh, OUTPUT_PATH):
        # utils.check_package_is_installed('igl')
        import igl

        logger.info('GeodesicsSolver')
        self.mesh = mesh
        self.OUTPUT_PATH = OUTPUT_PATH

        self.use_forwards_euler = True

        v, f = mesh.to_vertices_and_faces()
        v = np.array(v)
        f = np.array(f)

        # compute necessary data
        self.cotans = igl.cotmatrix_entries(v, f)  # compute_cotan_field(self.mesh)
        self.L = igl.cotmatrix(v, f)  # assemble_laplacian_matrix(self.mesh, self.cotans)
        self.M = igl.massmatrix(v, f)  # create_mass_matrix(mesh)

    def diffuse_heat(self, vi_sources, v_equalize=None, method='simulation'):
        """
        Heat diffusion.

        Attributes
        ----------
        vi_sources: list, int, the vertex indices of the sources
        v_equalize: list, int, the vertex indices whose value should be equalized
        method: str (Currently only 'simulation' works.)
        """
        if not v_equalize:
            v_equalize = []

        # First assign starting values (0 everywhere, 1 on the sources)
        u0 = np.zeros(len(list(self.mesh.vertices())))
        u0[vi_sources] = 1.0
        u = u0

        if method == 'default':  # This is buggy, does not keep boundary exactly on 0. TODO: INVESTIGATE
            t_mult = 1
            t = t_mult * np.mean(np.array([self.mesh.face_area(fkey) for fkey in self.mesh.faces()]))  # avg face area
            solver = scipy.sparse.linalg.factorized(self.M - t * self.L)  # pre-factor solver
            u = solver(u0)  # solve the heat equation: u = (VA - t * Lc) * u0

        elif method == 'simulation':
            u = u0

            for i in range(HEAT_DIFFUSION_ITERATIONS):
                if USE_FORWARDS_EULER:  # Forwards Euler (doesn't work so well)
                    u_prime = u + DELTA * self.L * u
                else:  # Backwards Euler
                    #  (M-delta*L) * u_prime = M*U
                    S = (self.M - DELTA * self.L)
                    b = self.M * u
                    u_prime = scipy.sparse.linalg.spsolve(S, b)

                if len(v_equalize) > 0:
                    u_prime[v_equalize] = np.min(u_prime[v_equalize])

                u = u_prime
                u[vi_sources] = 1.0  # make sure sources remain fixed to 1

        # reverse values (to make vstarts on 0)
        u = ([np.max(u)] * len(u)) - u

        utils.save_to_json([float(value) for value in u], self.OUTPUT_PATH, 'diffused_heat.json')
        return u

    def get_geodesic_distances(self, u, vi_sources, v_equalize=None):
        """
        Finds geodesic distances from heat distribution u. I

        Parameters
        ----------
        u: np.array, dimensions: V x 1 (one scalar value per vertex)
        vi_sources: list, int, the vertex indices of the sources
        v_equalize: list, int, the vertex indices whose value should be equalized
        """
        X = get_face_gradient_from_scalar_field(self.mesh, u)
        X = normalize_gradient(X)
        geodesic_dist = get_scalar_field_from_gradient(self.mesh, X, self.L, self.cotans)
        assert not math.isnan(geodesic_dist[0]), \
            "Attention, the 'get_scalar_field_from_gradient' function returned Nan. "
        geodesic_dist[vi_sources] = 0  # coerce boundary vertices to be on 0 (fixes small boundary imprecision)
        return geodesic_dist


if __name__ == "__main__":
    pass
