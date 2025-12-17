from __future__ import annotations

from typing import TYPE_CHECKING

from numpy.typing import NDArray

if TYPE_CHECKING:
    import numpy as np
    from compas.datastructures import Mesh


__all__ = ["get_heat_geodesic_distances"]


_cgal_solver_cache: dict[int, object] = {}


def get_heat_geodesic_distances(mesh: Mesh, vertices_start: list[int]) -> NDArray[np.floating]:
    """Calculate geodesic distances using CGAL heat method.

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
        Geodesic distance from sources to each vertex.

    """
    from compas_cgal.geodesics import HeatGeodesicSolver

    mesh_hash = hash((len(list(mesh.vertices())), len(list(mesh.faces()))))
    if mesh_hash not in _cgal_solver_cache:
        _cgal_solver_cache.clear()
        V, F = mesh.to_vertices_and_faces()
        _cgal_solver_cache[mesh_hash] = HeatGeodesicSolver((V, F))

    solver = _cgal_solver_cache[mesh_hash]
    return solver.solve(vertices_start)
