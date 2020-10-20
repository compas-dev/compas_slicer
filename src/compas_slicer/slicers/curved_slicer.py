from compas_slicer.slicers import BaseSlicer
from compas_slicer.slicers.curved_slicing import CompoundTarget
from compas_slicer.slicers.curved_slicing import find_desired_number_of_isocurves
import logging
from compas_slicer.slicers.curved_slicing import IsocurvesGenerator
from compas_slicer.utilities import save_to_json

logger = logging.getLogger('logger')

__all__ = ['CurvedSlicer']


class CurvedSlicer(BaseSlicer):
    """
    CurvedSlicer is....

    Attributes
    ----------
    mesh : compas.datastructures.Mesh
        Input mesh, it must be a triangular mesh (i.e. no quads or n-gons allowed)
    low_boundary_vs :
    high_boundary_vs :
    DATA_PATH :
    avg_layer_height :
    intermediary_outputs :
    """
    def __init__(self, mesh, low_boundary_vs, high_boundary_vs, DATA_PATH, avg_layer_height, intermediary_outputs=True):
        BaseSlicer.__init__(self, mesh)

        self.min_layer_height = 0.2
        self.max_layer_height = 2.0
        self.DATA_PATH = DATA_PATH
        self.avg_layer_height = avg_layer_height
        self.intermediary_outputs = intermediary_outputs

        #  --- Update vertex attributes
        self.mesh.update_default_vertex_attributes({'boundary': 0})
        for vkey, data in self.mesh.vertices(data=True):
            if vkey in low_boundary_vs:
                data['boundary'] = 1
            elif vkey in high_boundary_vs:
                data['boundary'] = 2

    def generate_paths(self):
        target_LOW = CompoundTarget(self.mesh, 'boundary', 1, self.DATA_PATH, is_smooth=False)
        target_HIGH = CompoundTarget(self.mesh, 'boundary', 2, self.DATA_PATH, is_smooth=False)

        target_HIGH.compute_uneven_boundaries_t_ends(target_LOW)
        if self.intermediary_outputs:
            target_LOW.save_distances("distances_LOW.json")
            target_HIGH.save_distances("distances_HIGH.json")
            target_HIGH.save_distances_clusters("distances_clusters_HIGH.json")
            save_to_json(target_HIGH.t_end_per_cluster, self.DATA_PATH, "t_end_per_cluster_HIGH.json")

        number_of_curves = find_desired_number_of_isocurves(target_LOW, target_HIGH, self.avg_layer_height)

        isocurves_generator = IsocurvesGenerator(self.mesh, target_LOW, target_HIGH, number_of_curves)
        self.layers = isocurves_generator.segments


if __name__ == "__main__":
    pass
