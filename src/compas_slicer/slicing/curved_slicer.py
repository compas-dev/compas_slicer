import sys, os
import compas_slicer

path_to_stratum = os.path.join(os.path.dirname(compas_slicer.__file__), '../../', 'submodules/stratum/src')
sys.path.append(path_to_stratum)
# import stratum

from compas_slicer.slicing import BaseSlicer
import compas_slicer.utilities.utils as utils
from compas.datastructures import Mesh
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
        pass


if __name__ == "__main__":
    print (os.path.join(os.path.dirname(compas_slicer.__file__)))
