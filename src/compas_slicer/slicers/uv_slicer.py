from compas_slicer.slicers import BaseSlicer
import logging
from compas_slicer.slicers.slice_utilities import UVContours
from compas_slicer.geometry import VerticalLayer, Path


import progressbar
from compas_slicer.geometry import VerticalLayersManager
from compas_slicer.parameters import get_param

logger = logging.getLogger('logger')

__all__ = ['UVSlicer']


class UVSlicer(BaseSlicer):

    def __init__(self, mesh, vkey_to_uv, no_of_isocurves, parameters=None):
        logger.info('UVSlicer')
        BaseSlicer.__init__(self, mesh)

        self.vkey_to_uv = vkey_to_uv
        self.no_of_isocurves = no_of_isocurves
        self.parameters = parameters if parameters else {}

        mesh.update_default_vertex_attributes({'uv': 0})
        for vkey in mesh.vertices():
            mesh.vertex_attribute(vkey, 'uv', self.vkey_to_uv[vkey])

    def generate_paths(self):
        """ Generates isocontours. """
        paths_type = 'flat'  # 'spiral' # 'zigzag' or 'zigzag'
        v_left, v_right = 0.0, 1.0 - 1e-4
        du = 1.0 / float(self.no_of_isocurves + 1)

        max_dist = get_param(self.parameters, key='vertical_layers_max_centroid_dist', defaults_type='curved_slicing')
        vertical_layers_manager = VerticalLayersManager(max_dist)

        # create paths + layers
        with progressbar.ProgressBar(max_value=self.no_of_isocurves) as bar:
            for i in range(1, self.no_of_isocurves + 1):

                if paths_type == 'spiral':
                    u1, u2 = i * du, i * du + du
                elif paths_type == 'zigzag':
                    u1 = i * du if i % 2 == 0 else i * du + du
                    u2 = i * du + du if i % 2 == 0 else i * du
                else:  # 'flat'
                    u1 = u2 = i * du

                p1 = (u1, v_left)
                p2 = (u2, v_right)

                contours = UVContours(self.mesh, p1, p2)
                contours.compute()
                contours.add_to_vertical_layers_manager(vertical_layers_manager)

                bar.update(i)  # advance progress bar

        self.layers = vertical_layers_manager.layers


if __name__ == "__main__":
    pass
