import numpy as np
import logging
from compas_slicer.pre_processing.curved_slicing_preprocessing import assign_distance_to_mesh_vertices, \
    compute_face_gradient, compute_vertex_gradient, normalize_gradient

logger = logging.getLogger('logger')
__all__ = ['GradientEvaluation']


class GradientEvaluation:
    def __init__(self, mesh, target_LOW=None, target_HIGH=None):
        print('')
        logger.info('Scalar field evaluation')
        self.mesh = mesh
        self.target_LOW = target_LOW
        self.target_HIGH = target_HIGH

        self.minima, self.maxima, self.saddles = [], [], []

        self.face_gradient = []
        self.vertex_gradient = []
        self.face_gradient_norm = []
        self.vertex_gradient_norm = []

        assign_distance_to_mesh_vertices(mesh, 0.5, target_LOW, target_HIGH)

    #####################################
    # --- Gradient manipulation
    # def manipulate_gradient(self):
    #     X = normalize_gradient(self.face_gradient)
    #     u = get_scalar_field_from_gradient()


    #####################################
    # --- Distance speed scalar evaluation

    def compute_norm_of_gradient(self):
        u_v = [self.mesh.vertex[vkey]["distance"] for vkey in self.mesh.vertices()]
        self.face_gradient = compute_face_gradient(self.mesh, u_v)
        self.vertex_gradient = compute_vertex_gradient(self.mesh, self.face_gradient)

        logger.info('Computing norm of gradient')
        f_g = np.array([self.face_gradient[i] for i, fkey in enumerate(self.mesh.faces())])
        v_g = np.array([self.vertex_gradient[i] for i, vkey in enumerate(self.mesh.vertices())])
        self.face_gradient_norm = list(np.linalg.norm(f_g, axis=1))
        self.vertex_gradient_norm = list(np.linalg.norm(v_g, axis=1))

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





if __name__ == "__main__":
    pass
