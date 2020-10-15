from compas_slicer.slicers import BaseSlicer
from compas_slicer.functionality import seams_align, unify_paths_orientation
from compas_slicer.slicers.curved_slicing import CompoundTarget
from compas_slicer.slicers.curved_slicing import find_desired_number_of_isocurves
import logging
from compas_slicer.slicers.curved_slicing import IsocurvesGenerator

logger = logging.getLogger('logger')

__all__ = ['CurvedSlicer']


class CurvedSlicer(BaseSlicer):
    def __init__(self, mesh, low_boundary_vs, high_boundary_vs, DATA_PATH, avg_layer_height):
        BaseSlicer.__init__(self, mesh)

        self.min_layer_height = 0.2
        self.max_layer_height = 2.0
        self.DATA_PATH = DATA_PATH
        self.avg_layer_height = avg_layer_height

        #  --- Update vertex attributes
        self.mesh.update_default_vertex_attributes({'boundary': 0})
        for vkey, data in self.mesh.vertices(data=True):
            if vkey in low_boundary_vs:
                data['boundary'] = 1
            elif vkey in high_boundary_vs:
                data['boundary'] = 2

    def split_regions(self):
        pass

    def slice_model(self):
        target_LOW = CompoundTarget(self.mesh, 'boundary', 1, self.DATA_PATH, is_smooth=False)
        target_HIGH = CompoundTarget(self.mesh, 'boundary', 2, self.DATA_PATH, is_smooth=False)

        target_HIGH.compute_uneven_boundaries_t_ends(target_LOW)
        target_LOW.save_distances("distances_0.json")
        target_HIGH.save_distances("distances_1.json")

        number_of_curves = find_desired_number_of_isocurves(target_LOW, target_HIGH, self.avg_layer_height)

        isocurves_generator = IsocurvesGenerator(self.mesh, target_LOW, target_HIGH, number_of_curves)
        self.layers = isocurves_generator.segments

        #  --- Align the seams between layers and unify orientation
        seams_align(self, align_with='x_axis')
        unify_paths_orientation(self)

        logger.info("Created %d VerticalLayers with %d total number of points"
                    % (len(self.layers), self.total_number_of_points))


if __name__ == "__main__":
    pass
