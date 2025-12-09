from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING, Literal

import numpy as np
import scipy
from numpy.typing import NDArray

import compas_slicer.utilities as utils
from compas_slicer.pre_processing.preprocessing_utils.gradient import (
    get_face_gradient_from_scalar_field,
    get_scalar_field_from_gradient,
    normalize_gradient,
)

if TYPE_CHECKING:
    from compas.datastructures import Mesh

logger = logging.getLogger('logger')

__all__ = ['get_heat_geodesic_distances',
           'get_custom_HEAT_geodesic_distances',
           'GeodesicsCache']


# CGAL heat method solver cache (for precomputation reuse)
_cgal_solver_cache: dict[int, object] = {}


def get_heat_geodesic_distances(
    mesh: Mesh, vertices_start: list[int]
) -> NDArray[np.floating]:
    """
    Calculate geodesic distances using CGAL heat method.

    Uses compas_cgal's HeatGeodesicSolver which provides CGAL's Heat_method_3
    implementation with intrinsic Delaunay triangulation.

    Parameters
    ----------
    mesh : Mesh
        A compas mesh (must be triangulated).
    vertices_start : list[int]
        Source vertex indices.

    Returns
    -------
    NDArray
        Minimum distance from any source to each vertex.
    """
    from compas_cgal.geodesics import HeatGeodesicSolver

    # Check if we have a cached solver for this mesh
    mesh_hash = hash((len(list(mesh.vertices())), len(list(mesh.faces()))))
    if mesh_hash not in _cgal_solver_cache:
        _cgal_solver_cache.clear()  # Clear old solvers
        _cgal_solver_cache[mesh_hash] = HeatGeodesicSolver(mesh)

    solver = _cgal_solver_cache[mesh_hash]

    # Compute distances for each source and take minimum
    all_distances = []
    for source in vertices_start:
        distances = solver.solve([source])
        all_distances.append(distances)

    return np.min(np.array(all_distances), axis=0)


# Backwards compatibility aliases
get_cgal_HEAT_geodesic_distances = get_heat_geodesic_distances
get_igl_HEAT_geodesic_distances = get_heat_geodesic_distances
get_igl_EXACT_geodesic_distances = get_heat_geodesic_distances


class GeodesicsCache:
    """Cache for geodesic distances to avoid redundant computations.

    Note: This class is kept for backwards compatibility but now uses CGAL.
    The CGAL solver has its own internal caching via _cgal_solver_cache.
    """

    def __init__(self) -> None:
        self._cache: dict[tuple[int, str], NDArray[np.floating]] = {}
        self._mesh_hash: int | None = None

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._mesh_hash = None

    def get_distances(
        self, mesh: Mesh, sources: list[int], method: str = 'heat'
    ) -> NDArray[np.floating]:
        """Get geodesic distances from sources, using cache when possible.

        Parameters
        ----------
        mesh : Mesh
            The mesh to compute distances on.
        sources : list[int]
            Source vertex indices.
        method : str
            Geodesic method (ignored, always uses CGAL heat method).

        Returns
        -------
        NDArray
            Minimum distance from any source to each vertex.
        """
        return get_heat_geodesic_distances(mesh, sources)


def get_custom_HEAT_geodesic_distances(
    mesh: Mesh,
    vi_sources: list[int],
    OUTPUT_PATH: str,
    v_equalize: list[int] | None = None,
    anisotropic_scaling: bool = False,
) -> NDArray[np.floating]:
    """ Calculate geodesic distances using the custom heat method. """
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

    def __init__(self, mesh: Mesh, OUTPUT_PATH: str) -> None:
        logger.info('GeodesicsSolver')
        self.mesh = mesh
        self.OUTPUT_PATH = OUTPUT_PATH

        self.use_forwards_euler = True

        # Compute matrices using NumPy implementations
        self.cotans = utils.get_mesh_cotans(mesh)
        self.L = utils.get_mesh_cotmatrix(mesh, fix_boundaries=False)
        self.M = utils.get_mesh_massmatrix(mesh)

    def diffuse_heat(
        self,
        vi_sources: list[int],
        v_equalize: list[int] | None = None,
        method: Literal['default', 'simulation'] = 'simulation',
    ) -> NDArray[np.floating]:
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

            # Pre-factor the matrix ONCE outside the loop (major speedup)
            if not USE_FORWARDS_EULER:
                S = self.M - DELTA * self.L
                solver = scipy.sparse.linalg.factorized(S)

            for _i in range(HEAT_DIFFUSION_ITERATIONS):
                if USE_FORWARDS_EULER:  # Forwards Euler (doesn't work so well)
                    u_prime = u + DELTA * self.L * u
                else:  # Backwards Euler - use pre-factored solver
                    b = self.M * u
                    u_prime = solver(b)

                if len(v_equalize) > 0:
                    u_prime[v_equalize] = np.min(u_prime[v_equalize])

                u = u_prime
                u[vi_sources] = 1.0  # make sure sources remain fixed to 1

        # reverse values (to make vstarts on 0)
        u = ([np.max(u)] * len(u)) - u

        utils.save_to_json([float(value) for value in u], self.OUTPUT_PATH, 'diffused_heat.json')
        return u

    def get_geodesic_distances(
        self, u: NDArray[np.floating], vi_sources: list[int], v_equalize: list[int] | None = None
    ) -> NDArray[np.floating]:
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
