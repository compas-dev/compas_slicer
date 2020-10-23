import numpy as np
import logging
from compas_slicer.slicers.curved_slicing import assign_distance_to_mesh_vertices

logger = logging.getLogger('logger')
__all__ = ['ScalarFieldEvaluation']


class ScalarFieldEvaluation:
    def __init__(self, mesh, target_LOW=None, target_HIGH=None):
        print('')
        logger.info('Scalar field evaluation')
        self.mesh = mesh
        self.target_LOW = target_LOW
        self.target_HIGH = target_HIGH

        self.minima, self.maxima, self.saddles = [], [], []
        self.face_scalars_flattened = []
        self.vertex_scalars_flattened = []

        assign_distance_to_mesh_vertices(mesh, 0.5, target_LOW, target_HIGH)

    #####################################
    # --- Distance speed scalar evaluation

    def compute_norm_of_gradient(self):
        u_v = [self.mesh.vertex[vkey]["distance"] for vkey in self.mesh.vertices()]
        face_gradient = compute_face_gradient(self.mesh, u_v)
        vertex_gradient = compute_vertex_gradient(self.mesh, face_gradient)

        self.face_scalars_flattened = [np.linalg.norm(face_gradient[i])
                                       for i, fkey in enumerate(self.mesh.faces())]
        self.vertex_scalars_flattened = [np.linalg.norm(vertex_gradient[i])
                                         for i, vkey in enumerate(self.mesh.vertices())]

    #####################################
    # --- Critical Points

    def find_critical_points(self):

        for vkey, data in self.mesh.vertices(data=True):
            current_v = data['distance']
            neighbors = self.mesh.vertex_neighbors(vkey, ordered=True)
            values = []
            neighbors.append(neighbors[0])
            for n in neighbors:
                v = self.mesh.vertex_attributes(n)['distance']
                if abs(v - current_v) > 0.0:
                    values.append(current_v - v)
            sgc = count_sign_changes(values)

            if sgc == 0:  # extreme point
                if current_v > self.mesh.vertex_attributes(neighbors[0])['distance']:
                    self.maxima.append(vkey)
                else:
                    self.minima.append(vkey)
            if sgc == 2:  # regular point
                pass
            if sgc > 2 and sgc % 2 == 0:
                self.saddles.append(vkey)


#####################################
# --- Helpers

def count_sign_changes(values):
    count = 0
    prev_v = 0
    for i, v in enumerate(values):
        if i == 0:
            prev_v = v
        else:
            if prev_v * v < 0:
                count += 1
            prev_v = v
    return count


def compute_vertex_gradient(mesh, face_gradient):
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
