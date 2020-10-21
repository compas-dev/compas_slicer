import numpy as np
import logging
from compas_slicer.slicers.curved_slicing import get_weighted_distance

logger = logging.getLogger('logger')
__all__ = ['ScalarFieldEvaluation']


class ScalarFieldEvaluation:
    def __init__(self, mesh, target_LOW=None, target_HIGH=None):
        logger.info('Scalar field evaluation')
        self.mesh = mesh
        self.target_LOW = target_LOW
        self.target_HIGH = target_HIGH

        self.face_scalars_flattened = []
        self.vertex_scalars_flattened = []

    def compute(self):
        self.add_exemplary_distance_attribute_on_vertices(t=0.5)
        self.add_distance_speed_scalar_evaluation()


    #####################################
    # --- Prepare vertex distance attributes
    def add_exemplary_distance_attribute_on_vertices(self, t=0.5):
        for i, vkey in enumerate(self.mesh.vertices()):
            d = get_weighted_distance(vkey, t, self.target_LOW, self.target_HIGH)
            self.mesh.vertex[vkey]["distance"] = d

    #####################################
    # --- Distance speed scalar evaluation

    def add_distance_speed_scalar_evaluation(self):
        self.mesh.update_default_face_attributes({'distance_speed_scalar': 0})
        self.mesh.update_default_vertex_attributes({'distance_speed_scalar': 0})

        scalar_dict = {}
        for i, fkey in enumerate(self.mesh.faces()):
            s = self.get_single_face_gradient(fkey)
            self.mesh.face_attributes(fkey)['distance_speed_scalar'] = s

        ## recompute all other info
        self.compute_vertex_scalars_on_mesh()
        self.face_scalars_flattened = [self.mesh.face_attributes(fkey)['distance_speed_scalar']
                                       for fkey in self.mesh.faces()]
        self.vertex_scalars_flattened = [self.mesh.vertex[vkey]['distance_speed_scalar']
                                         for vkey in self.mesh.vertices()]

    def get_single_face_gradient(self, fkey):
        edge_distances = [
            abs(self.mesh.vertex[u]["distance"] - self.mesh.vertex[v]["distance"]) / self.mesh.edge_length(u, v) \
            for u, v in self.mesh.face_halfedges(fkey)]

        d = max(edge_distances)
        return d

    def compute_vertex_scalars_on_mesh(self):
        for vkey in self.mesh.vertices():
            current_face_scalars = []
            current_face_areas = []
            for fkey in self.mesh.vertex_faces(vkey):
                current_face_scalars.append(self.mesh.face_attributes(fkey)["distance_speed_scalar"])
                current_face_areas.append(self.mesh.face_area(fkey))

            vs = 0
            for scalar, area in zip(current_face_scalars, current_face_areas):
                vs += scalar * area
            vertex_scalar = vs / np.sum(np.array(current_face_areas))
            # vertex_scalar = np.average(np.array(current_face_scalars))

            self.mesh.vertex[vkey]["distance_speed_scalar"] = vertex_scalar

    #####################################
    # --- Critical Points

    def find_critical_points(self):
        minima, maxima, saddles = [], [], []

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
                    maxima.append(vkey)
                else:
                    minima.append(vkey)
            if sgc == 2:  # regular point
                pass
            if sgc > 2 and sgc % 2 == 0:
                saddles.append(vkey)

        return minima, maxima, saddles


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
