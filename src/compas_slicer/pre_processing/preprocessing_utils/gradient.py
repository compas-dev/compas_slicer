import numpy as np
import logging
import scipy

logger = logging.getLogger('logger')

__all__ = ['get_vertex_gradient_from_face_gradient',
           'get_edge_gradient_from_vertex_gradient',
           'get_face_gradient_from_scalar_field',
           'normalize_gradient',
           'get_per_vertex_divergence',
           'get_scalar_field_from_gradient']


def get_vertex_gradient_from_face_gradient(mesh, face_gradient):
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


def get_edge_gradient_from_vertex_gradient(mesh, vertex_gradient):
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
    edge_gradient = []
    for u, v in mesh.edges():
        thisEdgeGradient = vertex_gradient[u] + vertex_gradient[v]
        edge_gradient.append(thisEdgeGradient)
    return np.array(edge_gradient)


def get_face_gradient_from_scalar_field(mesh, u, use_igl=True):
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
    if use_igl:
        try:
            import igl
            v, f = mesh.to_vertices_and_faces()
            G = igl.grad(np.array(v), np.array(f))
            X = G * u
            nf = len(list(mesh.faces()))
            X = np.array([[X[i], X[i + nf], X[i + 2 * nf]] for i in range(nf)])
            return X
        except ModuleNotFoundError:
            print("Could not calculate gradient with IGL because it is not installed. Falling back to default function")

        grad = []
        for fkey in mesh.faces():
            A = mesh.face_area(fkey)
            N = mesh.face_normal(fkey)
            edge_0, edge_1, edge_2 = get_face_edge_vectors(mesh, fkey)
            v0, v1, v2 = mesh.face_vertices(fkey)
            u0 = u[v0]
            u1 = u[v1]
            u2 = u[v2]
            vc0 = np.array(mesh.vertex_coordinates(v0))
            vc1 = np.array(mesh.vertex_coordinates(v1))
            vc2 = np.array(mesh.vertex_coordinates(v2))
            # grad_u = -1 * ((u1-u0) * np.cross(vc0-vc2, N) + (u2-u0) * np.cross(vc1-vc0, N)) / (2 * A)
            grad_u = ((u1-u0) * np.cross(vc0-vc2, N) + (u2-u0) * np.cross(vc1-vc0, N)) / (2 * A)
            # grad_u = (np.cross(N, edge_0) * u2 +
            #           np.cross(N, edge_1) * u0 +
            #           np.cross(N, edge_2) * u1) / (2 * A)
            grad.append(grad_u)
        return np.array(grad)


def get_face_edge_vectors(mesh, fkey):
    """ Returns the edge vectors of the face with fkey. """
    e0, e1, e2 = mesh.face_halfedges(fkey)
    edge_0 = np.array(mesh.vertex_coordinates(e0[0])) - np.array(mesh.vertex_coordinates(e0[1]))
    edge_1 = np.array(mesh.vertex_coordinates(e1[0])) - np.array(mesh.vertex_coordinates(e1[1]))
    edge_2 = np.array(mesh.vertex_coordinates(e2[0])) - np.array(mesh.vertex_coordinates(e2[1]))
    return edge_0, edge_1, edge_2


def get_per_vertex_divergence(mesh, X, cotans):
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


def normalize_gradient(X):
    """ Returns normalized gradient X. """
    norm = np.linalg.norm(X, axis=1)[..., np.newaxis]
    return X / norm  # normalize


def get_scalar_field_from_gradient(mesh, X, C, cotans):
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
    logger.info('Solved Δ(u) = div(X). Linear system error |Δ(u) - div(X)| = ' + str(np.linalg.norm(C * u - div_X)))
    u = u - np.amin(u)  # make start value equal 0
    u = 2*u
    return u


if __name__ == "__main__":
    pass
