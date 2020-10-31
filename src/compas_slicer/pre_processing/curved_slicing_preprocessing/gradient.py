import numpy as np
import logging
import scipy

logger = logging.getLogger('logger')

__all__ = ['compute_vertex_gradient',
           'compute_edge_gradient',
           'compute_face_gradient',
           'normalize_gradient']


def compute_vertex_gradient(mesh, face_gradient):
    logger.info('Computing per vertex gradient')
    vertex_gradient = []
    for v_key in mesh.vertices():
        faces_total_area = 0
        faces_total_grad = np.array([0.0, 0.0, 0.0])
        for f_key in mesh.vertex_faces(v_key):
            face_area = mesh.face_area(f_key)
            faces_total_area += face_area
            faces_total_grad += face_area * face_gradient[f_key, :]
        v_grad = faces_total_grad / faces_total_area
        vertex_gradient.append(v_grad)
    return np.array(vertex_gradient)


def compute_edge_gradient(mesh, vertex_gradient):
    edge_gradient = []
    for u, v in mesh.edges():
        thisEdgeGradient = vertex_gradient[u] + vertex_gradient[v]
        edge_gradient.append(thisEdgeGradient)
    return np.array(edge_gradient)


def compute_face_gradient(mesh, u):
    """ u is given per vertex """
    logger.info('Computing per face gradient')
    grad = []
    for fkey in mesh.faces():
        A = mesh.face_area(fkey)
        N = mesh.face_normal(fkey)
        edge_0, edge_1, edge_2 = get_face_edge_vectors(mesh, fkey)
        v0, v1, v2 = mesh.face_vertices(fkey)
        u0 = u[v0]
        u1 = u[v1]
        u2 = u[v2]
        grad_u = (np.cross(N, edge_0) * u2 +
                  np.cross(N, edge_1) * u0 +
                  np.cross(N, edge_2) * u1) / (2 * A)
        grad.append(grad_u)
    return np.array(grad)


def get_face_edge_vectors(mesh, fkey):
    e0, e1, e2 = mesh.face_halfedges(fkey)
    edge_0 = np.array(mesh.vertex_coordinates(e0[0])) - np.array(mesh.vertex_coordinates(e0[1]))
    edge_1 = np.array(mesh.vertex_coordinates(e1[0])) - np.array(mesh.vertex_coordinates(e1[1]))
    edge_2 = np.array(mesh.vertex_coordinates(e2[0])) - np.array(mesh.vertex_coordinates(e2[1]))
    return edge_0, edge_1, edge_2


def compute_per_face_divergence(mesh, X, cotans):
    cotans = cotans.reshape(-1, 3)
    div_X = np.zeros(len(list(mesh.vertices())))
    for fi, fkey in enumerate(mesh.faces()):
        x_fi = X[fi]
        edges = np.array(get_face_edge_vectors(mesh, fkey))
        for i in range(3):
            j = (i + 1) % 3
            k = (i + 2) % 3
            div_X[mesh.face_vertices(fkey)[i]] += cotans[fi, k] * np.dot(x_fi, edges[i]) / 2.0
            div_X[mesh.face_vertices(fkey)[i]] += cotans[fi, j] * np.dot(x_fi, -edges[k]) / 2.0
    return div_X


def normalize_gradient(g):
    return g / np.linalg.norm(g, axis=1)[..., np.newaxis]  # normalize


def get_scalar_field_from_gradient(g, mesh, L, cotans):
    div_X = compute_per_face_divergence(mesh, g, cotans)
    phi = scipy.sparse.linalg.spsolve(L, div_X)
    phi = phi - np.amin(phi)  # make start value equal 0
    return phi


if __name__ == "__main__":
    pass
