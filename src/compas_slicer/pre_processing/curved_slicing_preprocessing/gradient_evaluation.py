import numpy as np
import logging
import compas_slicer.utilities as utils
from compas_slicer.pre_processing.curved_slicing_preprocessing import assign_distance_to_mesh_vertices, \
    compute_face_gradient, compute_vertex_gradient

logger = logging.getLogger('logger')
__all__ = ['GradientEvaluation']


class GradientEvaluation:
    """ Evaluation of the gradient of the scalar function of the mesh.

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    DATA_PATH: str, path to the data folder
    weight:
    target_LOW: :class: 'compas_slicer.pre_processor.CompoundTarget'
    target_HIGH: :class: 'compas_slicer.pre_processor.CompoundTarget'
    """
    def __init__(self, mesh, DATA_PATH, weight=0.5, target_LOW=None, target_HIGH=None):
        print('')
        logger.info('Gradient evaluation')
        self.mesh = mesh
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
        self.target_LOW = target_LOW
        self.target_HIGH = target_HIGH

        self.minima, self.maxima, self.saddles = [], [], []

        self.face_gradient = []
        self.vertex_gradient = []
        self.face_gradient_norm = []
        self.vertex_gradient_norm = []

        assign_distance_to_mesh_vertices(mesh, weight, target_LOW, target_HIGH)

    @property
    def assigned_distances(self):
        """ Returns the distance values that have been assigned to the vertices for the evaluation. """
        return [data['get_distance'] for vkey, data in self.mesh.vertices(data=True)]

    #####################################
    # --- Distance speed scalar evaluation

    def compute_gradient(self):
        """ Computes the gradient on the faces and the vertices. """
        u_v = [self.mesh.vertex[vkey]["get_distance"] for vkey in self.mesh.vertices()]
        self.face_gradient = compute_face_gradient(self.mesh, u_v)
        self.vertex_gradient = compute_vertex_gradient(self.mesh, self.face_gradient)

    def compute_gradient_norm(self):
        """ Computes the norm of the gradient. """
        logger.info('Computing norm of gradient')
        f_g = np.array([self.face_gradient[i] for i, fkey in enumerate(self.mesh.faces())])
        v_g = np.array([self.vertex_gradient[i] for i, vkey in enumerate(self.mesh.vertices())])
        self.face_gradient_norm = list(np.linalg.norm(f_g, axis=1))
        self.vertex_gradient_norm = list(np.linalg.norm(v_g, axis=1))

    #####################################
    # --- Critical Points

    def find_critical_points(self):
        """ Finds minima, maxima and saddle points of the scalar function on the mesh. """
        for vkey, data in self.mesh.vertices(data=True):
            current_v = data['get_distance']
            neighbors = self.mesh.vertex_neighbors(vkey, ordered=True)
            values = []
            if len(neighbors) > 0:
                neighbors.append(neighbors[0])
                for n in neighbors:
                    v = self.mesh.vertex_attributes(n)['get_distance']
                    if abs(v - current_v) > 0.0:
                        values.append(current_v - v)
                sgc = count_sign_changes(values)

                if sgc == 0:  # extreme point
                    if current_v > self.mesh.vertex_attributes(neighbors[0])['get_distance']:
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
    """ Returns the number of sign changes in a list of values. """
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
