"""Vectorized numpy operations for performance-critical computations."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.spatial import cKDTree


def batch_closest_points(
    query_pts: NDArray[np.float64],
    target_pts: NDArray[np.float64],
) -> tuple[NDArray[np.intp], NDArray[np.float64]]:
    """Find closest points using KDTree for efficient batch queries.

    Parameters
    ----------
    query_pts : ndarray (N, 3)
        Points to query.
    target_pts : ndarray (M, 3)
        Target point cloud.

    Returns
    -------
    indices : ndarray (N,)
        Index of closest target point for each query.
    distances : ndarray (N,)
        Distance to closest point.
    """
    tree = cKDTree(target_pts)
    distances, indices = tree.query(query_pts)
    return indices, distances


def vertex_gradient_from_face_gradient(
    V: NDArray[np.float64],
    F: NDArray[np.intp],
    face_gradient: NDArray[np.float64],
    face_areas: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Compute per-vertex gradient from face gradients using area weighting.

    Vectorized version: accumulates face contributions to vertices using numpy.

    Parameters
    ----------
    V : ndarray (V, 3)
        Vertex coordinates.
    F : ndarray (F, 3)
        Face vertex indices.
    face_gradient : ndarray (F, 3)
        Gradient vector per face.
    face_areas : ndarray (F,)
        Area per face.

    Returns
    -------
    ndarray (V, 3)
        Gradient vector per vertex.
    """
    n_vertices = len(V)

    # Weight gradients by area
    weighted_gradients = face_gradient * face_areas[:, np.newaxis]  # (F, 3)

    # Accumulate to vertices using np.add.at
    vertex_grad_sum = np.zeros((n_vertices, 3), dtype=np.float64)
    vertex_area_sum = np.zeros(n_vertices, dtype=np.float64)

    for i in range(3):  # For each vertex of each face
        np.add.at(vertex_grad_sum, F[:, i], weighted_gradients)
        np.add.at(vertex_area_sum, F[:, i], face_areas)

    # Avoid division by zero
    vertex_area_sum = np.maximum(vertex_area_sum, 1e-10)

    return vertex_grad_sum / vertex_area_sum[:, np.newaxis]


def edge_gradient_from_vertex_gradient(
    edges: NDArray[np.intp],
    vertex_gradient: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Compute edge gradient as sum of endpoint vertex gradients.

    Parameters
    ----------
    edges : ndarray (E, 2)
        Edge vertex indices.
    vertex_gradient : ndarray (V, 3)
        Gradient per vertex.

    Returns
    -------
    ndarray (E, 3)
        Gradient per edge.
    """
    return vertex_gradient[edges[:, 0]] + vertex_gradient[edges[:, 1]]


def face_gradient_from_scalar_field(
    V: NDArray[np.float64],
    F: NDArray[np.intp],
    scalar_field: NDArray[np.float64],
    face_normals: NDArray[np.float64],
    face_areas: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Compute per-face gradient from vertex scalar field.

    Vectorized computation using the formula:
    grad_u = ((u1-u0) * cross(v0-v2, N) + (u2-u0) * cross(v1-v0, N)) / (2*A)

    Parameters
    ----------
    V : ndarray (V, 3)
        Vertex coordinates.
    F : ndarray (F, 3)
        Face vertex indices.
    scalar_field : ndarray (V,)
        Scalar value per vertex.
    face_normals : ndarray (F, 3)
        Normal vector per face.
    face_areas : ndarray (F,)
        Area per face.

    Returns
    -------
    ndarray (F, 3)
        Gradient vector per face.
    """
    # Get vertex coordinates for each face
    v0 = V[F[:, 0]]  # (F, 3)
    v1 = V[F[:, 1]]  # (F, 3)
    v2 = V[F[:, 2]]  # (F, 3)

    # Get scalar values for each face vertex
    u0 = scalar_field[F[:, 0]]  # (F,)
    u1 = scalar_field[F[:, 1]]  # (F,)
    u2 = scalar_field[F[:, 2]]  # (F,)

    # Compute cross products
    cross1 = np.cross(v0 - v2, face_normals)  # (F, 3)
    cross2 = np.cross(v1 - v0, face_normals)  # (F, 3)

    # Compute gradient
    grad = (
        (u1 - u0)[:, np.newaxis] * cross1 + (u2 - u0)[:, np.newaxis] * cross2
    ) / (2 * face_areas[:, np.newaxis])

    return grad


def per_vertex_divergence(
    V: NDArray[np.float64],
    F: NDArray[np.intp],
    X: NDArray[np.float64],
    cotans: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Compute divergence of face gradient field at each vertex.

    Parameters
    ----------
    V : ndarray (V, 3)
        Vertex coordinates.
    F : ndarray (F, 3)
        Face vertex indices.
    X : ndarray (F, 3)
        Gradient vector per face.
    cotans : ndarray (F, 3)
        Cotangent weights per face edge.

    Returns
    -------
    ndarray (V,)
        Divergence value per vertex.
    """
    n_vertices = len(V)

    # Get vertex coordinates for each face
    v0 = V[F[:, 0]]  # (F, 3)
    v1 = V[F[:, 1]]  # (F, 3)
    v2 = V[F[:, 2]]  # (F, 3)

    # Edge vectors (opposite to vertex i)
    e0 = v1 - v2  # edge opposite to v0
    e1 = v2 - v0  # edge opposite to v1
    e2 = v0 - v1  # edge opposite to v2

    # Compute dot products with gradient
    dot0 = np.einsum('ij,ij->i', X, e0)  # (F,)
    dot1 = np.einsum('ij,ij->i', X, e1)  # (F,)
    dot2 = np.einsum('ij,ij->i', X, e2)  # (F,)

    # Cotangent contributions (cotans[f, i] is cotan of angle at vertex i)
    # For vertex i: contrib = cotan[k] * dot(X, e_i) + cotan[j] * dot(X, -e_k)
    # where j = (i+1)%3, k = (i+2)%3
    contrib0 = (cotans[:, 2] * dot0 + cotans[:, 1] * (-dot2)) / 2.0
    contrib1 = (cotans[:, 0] * dot1 + cotans[:, 2] * (-dot0)) / 2.0
    contrib2 = (cotans[:, 1] * dot2 + cotans[:, 0] * (-dot1)) / 2.0

    # Accumulate to vertices
    div_X = np.zeros(n_vertices, dtype=np.float64)
    np.add.at(div_X, F[:, 0], contrib0)
    np.add.at(div_X, F[:, 1], contrib1)
    np.add.at(div_X, F[:, 2], contrib2)

    return div_X


def vectorized_distances(
    points1: NDArray[np.float64],
    points2: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Compute pairwise distances between two point sets.

    Parameters
    ----------
    points1 : ndarray (N, 3)
    points2 : ndarray (M, 3)

    Returns
    -------
    ndarray (N, M)
        Distance matrix.
    """
    # Using broadcasting: (N, 1, 3) - (1, M, 3) = (N, M, 3)
    diff = points1[:, np.newaxis, :] - points2[np.newaxis, :, :]
    return np.linalg.norm(diff, axis=2)


def min_distances_to_set(
    query_pts: NDArray[np.float64],
    target_pts: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Compute minimum distance from each query point to target set.

    More memory efficient than full distance matrix for large sets.

    Parameters
    ----------
    query_pts : ndarray (N, 3)
    target_pts : ndarray (M, 3)

    Returns
    -------
    ndarray (N,)
        Minimum distance for each query point.
    """
    tree = cKDTree(target_pts)
    distances, _ = tree.query(query_pts)
    return distances
