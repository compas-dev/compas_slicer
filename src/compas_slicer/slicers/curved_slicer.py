from compas_slicer.slicers import BaseSlicer
from compas_slicer.geometry import VerticalLayer
import compas_slicer.utilities as utils
from compas_slicer.geometry import Path
from compas_slicer.slicers.curved_slicing import CompoundTarget
from compas_slicer.slicers.curved_slicing import find_desired_number_of_isocurves
import logging

logger = logging.getLogger('logger')

packages = utils.TerminalCommand('conda list').get_split_output_strings()


__all__ = ['CurvedSlicer']


class CurvedSlicer(BaseSlicer):
    def __init__(self, mesh, low_boundary_vs, high_boundary_vs, DATA_PATH):
        BaseSlicer.__init__(self, mesh)

        self.min_layer_height = 0.2
        self.max_layer_height = 2.0
        self.DATA_PATH = DATA_PATH

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

        #  Marching Triangles
        number_of_curves = find_desired_number_of_isocurves(target_LOW, target_HIGH, avg_layer_height=1.1)

        isocurves_generator = IsocurvesGenerator(self.mesh, target_LOW, target_HIGH, number_of_curves)

        marching_triangles = MarchingTriangles


        #  Save to Json
        stratum_utils.isocurves_segments_to_json(marching_triangles.segments, self.DATA_PATH,
                                                 "isocurves_segments.json")

        #  convert stratum entities to compas_slicer entities
        segments = []
        for i, stratum_segment in enumerate(marching_triangles.segments):
            s = VerticalLayer(i)
            segments.append(s)
            for isocurve in stratum_segment.isocurves:
                s.append_(Path(isocurve.points, is_closed=True))

        self.layers = segments


if __name__ == "__main__":
    pass
