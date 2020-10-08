import sys

from compas_slicer.slicers import BaseSlicer
from compas_slicer.geometry import VerticalLayer
import compas_slicer.utilities as utils
from compas_slicer.geometry import Path
from compas.plugins import PluginNotInstalledError

import logging

logger = logging.getLogger('logger')

packages = utils.TerminalCommand('conda list').get_split_output_strings()
if 'stratum' in packages:
    from stratum.isocurves.compound_target import CompoundTarget
    from stratum.isocurves.marching_triangles import MarchingTriangles, find_desired_number_of_isocurves
    import stratum.utils.utils as stratum_utils

__all__ = ['CurvedSlicer']


class CurvedSlicer(BaseSlicer):
    def __init__(self, mesh, low_boundary_vs, high_boundary_vs, DATA_PATH):
        if 'stratum' not in packages:
            raise PluginNotInstalledError("--------ATTENTION! ----------- \
                            STRATUM library (for curved slicing) is missing! \
                            You can't use this slicer without it. \
                            Check the README for instructions.")

        BaseSlicer.__init__(self, mesh)

        if not 'stratum' in sys.modules:
            for key in sys.modules:
                print(key)
            raise ValueError('Attention! You need to install stratum to use the curved slicer')

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

    def split_regions(self):
        pass

    def slice_model(self):
        target_LOW = CompoundTarget(self.mesh, 'boundary', 1, self.DATA_PATH, is_smooth=False)
        target_HIGH = CompoundTarget(self.mesh, 'boundary', 2, self.DATA_PATH, is_smooth=False)
        target_HIGH.compute_uneven_boundaries_t_ends(target_LOW)
        target_LOW.save_distances("distances_0.json")
        target_HIGH.save_distances("distances_1.json")

        ## Marching Triangles
        print('')
        number_of_curves = find_desired_number_of_isocurves(target_LOW, target_HIGH)
        marching_triangles = MarchingTriangles(self.mesh, target_LOW, target_HIGH, number_of_curves)

        ## Save to Json
        stratum_utils.isocurves_segments_to_json(marching_triangles.segments, self.DATA_PATH,
                                                 "isocurves_segments.json")

        ## convert stratum entities to compas_slicer entities
        segments = []  ## path collections (vertical sorting)
        for i, stratum_segment in enumerate(marching_triangles.segments):
            s = VerticalLayer(i)
            segments.append(s)
            for isocurve in stratum_segment.isocurves:
                s.append_(Path(isocurve.points, is_closed=True))

        self.layers = segments


if __name__ == "__main__":
    pass
