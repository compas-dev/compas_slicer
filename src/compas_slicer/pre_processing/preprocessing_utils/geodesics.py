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

__all__ = ['get_igl_EXACT_geodesic_distances',
           'get_custom_HEAT_geodesic_distances',
           'GeodesicsCache']


class GeodesicsCache:
    """Cache for geodesic distances to avoid redundant computations.

    The libigl exact geodesic method is expensive (~80ms per call).
    This cache stores per-source distances and reuses them.
    """

    def __init__(self) -> None:
        self._cache: dict[int, NDArray[np.floating]] = {}
        self._mesh_hash: int | None = None

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._mesh_hash = None

    def get_distances(
        self, mesh: Mesh, sources: list[int], method: str = 'exact'
    ) -> NDArray[np.floating]:
        """Get geodesic distances from sources, using cache when possible.

        Parameters
        ----------
        mesh : Mesh
            The mesh to compute distances on.
        sources : list[int]
            Source vertex indices.
        method : str
            Geodesic method ('exact' or 'heat').

        Returns
        -------
        NDArray
            Minimum distance from any source to each vertex.
        """
        from compas_libigl.geodistance import trimesh_geodistance

        # Check if mesh changed (simple hash based on vertex count)
        mesh_hash = hash((len(list(mesh.vertices())), len(list(mesh.faces()))))
        if mesh_hash != self._mesh_hash:
            self.clear()
            self._mesh_hash = mesh_hash

        M = mesh.to_vertices_and_faces()
        all_distances = []

        for source in sources:
            cache_key = (source, method)
            if cache_key not in self._cache:
                distances = trimesh_geodistance(M, source, method=method)
                self._cache[cache_key] = np.array(distances)
            all_distances.append(self._cache[cache_key])

        return np.min(np.array(all_distances), axis=0)


# Global cache instance
_geodesics_cache = GeodesicsCache()


def get_igl_EXACT_geodesic_distances(
    mesh: Mesh, vertices_start: list[int]
) -> NDArray[np.floating]:
    """
    Calculate geodesic distances using compas_libigl.

    Uses caching to avoid redundant computations when the same
    source vertices are queried multiple times.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    vertices_start: list, int
    """
    return _geodesics_cache.get_distances(mesh, vertices_start, method='exact')


def get_custom_HEAT_geodesic_distances(
    mesh: Mesh,
    vi_sources: list[int],
    OUTPUT_PATH: str,
    v_equalize: list[int] | None = None,
    anisotropic_scaling: bool = False,
) -> NDArray[np.floating]:
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

    def __init__(self, mesh: Mesh, OUTPUT_PATH: str) -> None:
        from compas_libigl.cotmatrix import trimesh_cotmatrix, trimesh_cotmatrix_entries
        from compas_libigl.massmatrix import trimesh_massmatrix

        logger.info('GeodesicsSolver')
        self.mesh = mesh
        self.OUTPUT_PATH = OUTPUT_PATH

        self.use_forwards_euler = True

        M = mesh.to_vertices_and_faces()

        # compute necessary data using compas_libigl
        self.cotans = trimesh_cotmatrix_entries(M)
        self.L = trimesh_cotmatrix(M)
        self.M = trimesh_massmatrix(M)

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
