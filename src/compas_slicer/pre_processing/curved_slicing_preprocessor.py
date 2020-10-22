from compas_slicer.pre_processing import CompoundTarget
from compas_slicer.pre_processing import ScalarFieldEvaluation
from compas_slicer.utilities import save_to_json

__all__ = ['CurvedSlicingPreprocessor']


class CurvedSlicingPreprocessor:
    def __init__(self, mesh, low_boundary_vs, high_boundary_vs, parameters, DATA_PATH):
        self.mesh = mesh
        self.parameters = parameters
        self.DATA_PATH = DATA_PATH

        self.target_LOW = None
        self.target_HIGH = None

        #  --- Update vertex attributes
        self.mesh.update_default_vertex_attributes({'boundary': 0})
        for vkey, data in self.mesh.vertices(data=True):
            if vkey in low_boundary_vs:
                data['boundary'] = 1
            elif vkey in high_boundary_vs:
                data['boundary'] = 2

        self.create_compound_targets()

    def create_compound_targets(self):
        is_smooth, r = self.parameters['target_LOW_smooth'][0], self.parameters['target_LOW_smooth'][1]
        self.target_LOW = CompoundTarget(self.mesh, 'boundary', 1, self.DATA_PATH, is_smooth=is_smooth, r=r)
        is_smooth, r = self.parameters['target_HIGH_smooth'][0], self.parameters['target_HIGH_smooth'][1]
        self.target_HIGH = CompoundTarget(self.mesh, 'boundary', 2, self.DATA_PATH, is_smooth=is_smooth, r=r)
        self.target_HIGH.compute_uneven_boundaries_t_ends(self.target_LOW)
        #  --- save intermediary distance outputs
        if self.parameters['create_intermediary_outputs']:
            self.target_LOW.save_distances("distances_LOW.json")
            self.target_HIGH.save_distances("distances_HIGH.json")
            self.target_HIGH.save_distances_clusters("distances_clusters_HIGH.json")
            save_to_json(self.target_HIGH.t_end_per_cluster, self.DATA_PATH, "t_end_per_cluster_HIGH.json")

    def scalar_field_evaluation(self):
        s = ScalarFieldEvaluation(self.mesh, self.target_LOW, self.target_HIGH)
        s.compute_distance_speed_scalar()
        minima, maxima, saddles = s.find_critical_points()
        if self.parameters['create_intermediary_outputs']:
            save_to_json(s.vertex_scalars_flattened, self.DATA_PATH, 'vertex_scalar_field_evaluation.json')
            save_to_json(minima, self.DATA_PATH, "minima.json")
            save_to_json(maxima, self.DATA_PATH, "maxima.json")
            save_to_json(saddles, self.DATA_PATH, "saddles.json")
