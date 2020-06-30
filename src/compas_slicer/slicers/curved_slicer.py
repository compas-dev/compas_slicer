import sys, os
import compas_slicer

# path_to_stratum = os.path.join(os.path.dirname(compas_slicer.__file__), '../../', 'dependencies/stratum/src')
# sys.path.append(path_to_stratum)
import stratum

from stratum.isocurves.compound_target import CompoundTarget
from stratum.isocurves.marching_triangles import MarchingTriangles, find_desired_number_of_isocurves
import stratum.utils.utils as stratum_utils
from compas_slicer.slicers import BaseSlicer
from compas_slicer.geometry import Segment, Path
# import compas_slicer.utilities.utils as utils
import logging

logger = logging.getLogger('logger')

__all__ = ['CurvedSlicer']


class CurvedSlicer(BaseSlicer):
    def __init__(self, mesh, low_boundary_vs, high_boundary_vs, DATA_PATH):
        BaseSlicer.__init__(self, mesh)

        self.min_layer_height = 0.2
        self.max_layer_height = 2.0
        self.DATA_PATH = DATA_PATH

        ### --- Update vertex attributes
        self.mesh.update_default_vertex_attributes({'boundary': 0})
        for vkey, data in self.mesh.vertices(data=True):
            if vkey in low_boundary_vs:
                data['boundary'] = 1
            elif vkey in high_boundary_vs:
                data['boundary'] = 2

    def slice_model(self, create_contours=True, create_infill=False, create_supports=False):
        if create_infill or create_supports:
            raise NotImplementedError

        if create_contours:
            target_0 = CompoundTarget(self.mesh, 'boundary', 1, self.DATA_PATH, is_smooth=False)
            target_1 = CompoundTarget(self.mesh, 'boundary', 2, self.DATA_PATH, is_smooth=False)
            target_0.save_distances("distances_0.json")
            target_1.save_distances("distances_1.json")

            ## --- Marching Triangles
            number_of_curves = find_desired_number_of_isocurves(target_0, target_1)
            marching_triangles = MarchingTriangles(self.mesh, target_0, target_1, number_of_curves)
            stratum_utils.isocurves_segments_to_json(marching_triangles.segments, self.DATA_PATH, "isocurves_segments.json")

            ## convert stratum entities to compas_slicer entities
            segments = []
            for i, stratum_segment in enumerate(marching_triangles.segments):
                s = Segment(i)
                segments.append(s)
                for isocurve in stratum_segment.isocurves:
                    s.append_(Path(isocurve.points, is_closed=True))

            self.print_paths = segments

if __name__ == "__main__":
    pass
