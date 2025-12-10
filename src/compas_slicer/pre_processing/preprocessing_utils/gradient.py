from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import scipy
from loguru import logger
from numpy.typing import NDArray

if TYPE_CHECKING:
    from compas.datastructures import Mesh

from compas_slicer._numpy_ops import edge_gradient_from_vertex_gradient as _edge_gradient_vectorized
from compas_slicer._numpy_ops import face_gradient_from_scalar_field as _face_gradient_vectorized
from compas_slicer._numpy_ops import per_vertex_divergence as _divergence_vectorized
from compas_slicer._numpy_ops import vertex_gradient_from_face_gradient as _vertex_gradient_vectorized

__all__ = ['get_vertex_gradient_from_face_gradient',
           'get_edge_gradient_from_vertex_gradient',
           'get_face_gradient_from_scalar_field',
           'normalize_gradient',
           'get_per_vertex_divergence',
           'get_scalar_field_from_gradient']


def _mesh_to_arrays(mesh: Mesh) -> tuple[NDArray[np.floating], NDArray[np.intp]]:
    """Convert COMPAS mesh to numpy arrays for vectorized operations."""
    V = np.array([mesh.vertex_coordinates(v) for v in mesh.vertices()], dtype=np.float64)
    F = np.array([mesh.face_vertices(f) for f in mesh.faces()], dtype=np.intp)
    return V, F


def get_vertex_gradient_from_face_gradient(
    mesh: Mesh, face_gradient: NDArray[np.floating]
) -> NDArray[np.floating]:
    """
    Finds vertex gradient given an already calculated per face gradient.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    face_gradient: np.array with one vec3 per face of the mesh. (dimensions : #F x 3)

    Returns
    ----------
    np.array (dimensions : #V x 3) one gradient vector per vertex.
    """
    logger.info('Computing per vertex gradient')
    V, F = _mesh_to_arrays(mesh)
    face_areas = np.array([mesh.face_area(f) for f in mesh.faces()], dtype=np.float64)
    return _vertex_gradient_vectorized(V, F, face_gradient, face_areas)


def get_edge_gradient_from_vertex_gradient(
    mesh: Mesh, vertex_gradient: NDArray[np.floating]
) -> NDArray[np.floating]:
    """
    Finds edge gradient given an already calculated per vertex gradient.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    vertex_gradient: np.array with one vec3 per vertex of the mesh. (dimensions : #V x 3)

    Returns
    ----------
    np.array (dimensions : #E x 3) one gradient vector per edge.
    """
    edges = np.array(list(mesh.edges()), dtype=np.intp)
    return _edge_gradient_vectorized(edges, vertex_gradient)


def get_face_gradient_from_scalar_field(
    mesh: Mesh, u: NDArray[np.floating]
) -> NDArray[np.floating]:
    """
    Finds face gradient from scalar field u.
    Scalar field u is given per vertex.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    u: list, float. (dimensions : #VN x 1)

    Returns
    ----------
    np.array (dimensions : #F x 3) one gradient vector per face.
    """
    logger.info('Computing per face gradient')
    V, F = _mesh_to_arrays(mesh)
    scalar_field = np.asarray(u, dtype=np.float64)
    face_normals = np.array([mesh.face_normal(f) for f in mesh.faces()], dtype=np.float64)
    face_areas = np.array([mesh.face_area(f) for f in mesh.faces()], dtype=np.float64)
    return _face_gradient_vectorized(V, F, scalar_field, face_normals, face_areas)


def get_face_edge_vectors(
    mesh: Mesh, fkey: int
) -> tuple[NDArray[np.floating], NDArray[np.floating], NDArray[np.floating]]:
    """ Returns the edge vectors of the face with fkey. """
    e0, e1, e2 = mesh.face_halfedges(fkey)
    edge_0 = np.array(mesh.vertex_coordinates(e0[0])) - np.array(mesh.vertex_coordinates(e0[1]))
    edge_1 = np.array(mesh.vertex_coordinates(e1[0])) - np.array(mesh.vertex_coordinates(e1[1]))
    edge_2 = np.array(mesh.vertex_coordinates(e2[0])) - np.array(mesh.vertex_coordinates(e2[1]))
    return edge_0, edge_1, edge_2


def get_per_vertex_divergence(
    mesh: Mesh, X: NDArray[np.floating], cotans: NDArray[np.floating]
) -> NDArray[np.floating]:
    """
    Computes the divergence of the gradient X for the mesh, using cotangent weights.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    X: np.array, (dimensions: #F x 3), per face gradient
    cotans:  np.array, (dimensions: #F x 3), 1/2*cotangents corresponding angles

    Returns
    ----------
    np.array (dimensions : #V x 1) one float (divergence value) per vertex.
    """
    V, F = _mesh_to_arrays(mesh)
    cotans = cotans.reshape(-1, 3)
    return _divergence_vectorized(V, F, X, cotans)


def normalize_gradient(X: NDArray[np.floating]) -> NDArray[np.floating]:
    """ Returns normalized gradient X. """
    norm = np.linalg.norm(X, axis=1)[..., np.newaxis]
    return X / norm  # normalize


def get_scalar_field_from_gradient(
    mesh: Mesh,
    X: NDArray[np.floating],
    C: scipy.sparse.csr_matrix,
    cotans: NDArray[np.floating],
) -> NDArray[np.floating]:
    """
    Find scalar field u that best explains gradient X.
    Laplacian(u) = Divergence(X).
    This defines a scalar field up to translation, then we subtract the min to make sure it starts from 0.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    X: np.array, (dimensions: #F x 3), per face gradient
    C: 'scipy.sparse.csr_matrix',
        sparse matrix (dimensions: #V x #V), cotmatrix, each row i corresponding to v(i, :)
    cotans: np.array, (dimensions: #F x 3), 1/2*cotangents corresponding angles

    Returns
    ----------
    np.array (dimensions : #V x 1) one scalar value per vertex.
    """
    div_X = get_per_vertex_divergence(mesh, X, cotans)
    u = scipy.sparse.linalg.spsolve(C, div_X)
    logger.info(f'Solved Δ(u) = div(X). Linear system error |Δ(u) - div(X)| = {np.linalg.norm(C * u - div_X):.6e}')
    u = u - np.amin(u)  # make start value equal 0
    u = 2*u
    return u


if __name__ == "__main__":
    pass
