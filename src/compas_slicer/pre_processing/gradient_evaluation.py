import numpy as np
import logging
import compas_slicer.utilities as utils
from compas_slicer.pre_processing.preprocessing_utils import get_face_gradient_from_scalar_field
from compas_slicer.pre_processing.preprocessing_utils import get_vertex_gradient_from_face_gradient

logger = logging.getLogger('logger')

__all__ = ['GradientEvaluation']


class GradientEvaluation(object):
    """
    Evaluation of the gradient of the scalar function of the mesh.
    The scalar function should be stored as a vertex attribute on every vertex, with key='scalar_field'

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    DATA_PATH: str, path to the data folder

    """
    def __init__(self, mesh, DATA_PATH):
        for v_key, data in mesh.vertices(data=True):
            assert 'scalar_field' in data, "Vertex %d does not have the attribute 'scalar_field'"

        print('')
        logger.info('Gradient evaluation')
        self.mesh = mesh
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)

        self.minima, self.maxima, self.saddles = [], [], []

        self.face_gradient = []  # np.array (#F x 3) one gradient vector per face.
        self.vertex_gradient = []  # np.array (#V x 3) one gradient vector per vertex.
        self.face_gradient_norm = []  # list (#F x 1)
        self.vertex_gradient_norm = []  # list (#V x 1)

    def compute_gradient(self):
        """ Computes the gradient on the faces and the vertices. """
        u_v = [self.mesh.vertex[vkey]['scalar_field'] for vkey in self.mesh.vertices()]
        self.face_gradient = get_face_gradient_from_scalar_field(self.mesh, u_v)
        self.vertex_gradient = get_vertex_gradient_from_face_gradient(self.mesh, self.face_gradient)

    def compute_gradient_norm(self):
        """ Computes the norm of the gradient. """
        logger.info('Computing norm of gradient')
        f_g = np.array([self.face_gradient[i] for i, fkey in enumerate(self.mesh.faces())])
        v_g = np.array([self.vertex_gradient[i] for i, vkey in enumerate(self.mesh.vertices())])
        self.face_gradient_norm = list(np.linalg.norm(f_g, axis=1))
        self.vertex_gradient_norm = list(np.linalg.norm(v_g, axis=1))

    def find_critical_points(self):
        """ Finds minima, maxima and saddle points of the scalar function on the mesh. """
        for vkey, data in self.mesh.vertices(data=True):
            current_v = data['scalar_field']
            neighbors = self.mesh.vertex_neighbors(vkey, ordered=True)
            values = []
            if len(neighbors) > 0:
                neighbors.append(neighbors[0])
                for n in neighbors:
                    v = self.mesh.vertex_attributes(n)['scalar_field']
                    if abs(v - current_v) > 0.0:
                        values.append(current_v - v)
                sgc = count_sign_changes(values)

                if sgc == 0:  # extreme point
                    if current_v > self.mesh.vertex_attributes(neighbors[0])['scalar_field']:
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
