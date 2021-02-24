import numpy as np
from compas_slicer.slicers import BaseSlicer
import logging
from compas_slicer.slicers.slice_utilities import ScalarFieldContours
import progressbar
from compas_slicer.geometry import VerticalLayersManager
from compas_slicer.parameters import get_param

logger = logging.getLogger('logger')

__all__ = ['ScalarFieldSlicer']


class ScalarFieldSlicer(BaseSlicer):
    """
    Generates the isocontours of a scalar field defined on the mesh vertices.

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
        Input mesh, it must be a triangular mesh (i.e. no quads or n-gons allowed)
        Note that the topology of the mesh matters, irregular tesselation can lead to undesired results.
        We recommend to 1)re-topologize, 2) triangulate, and 3) weld your mesh in advance.
    scalar_field: list, Vx1 (one float per vertex that represents the scalar field)
    no_of_isocurves: int, how many isocontours to be generated
    """

    def __init__(self, mesh, scalar_field, no_of_isocurves, parameters=None):
        logger.info('ScalarFieldSlicer')
        BaseSlicer.__init__(self, mesh)

        self.no_of_isocurves = no_of_isocurves
        self.scalar_field = list(np.array(scalar_field) - np.min(np.array(scalar_field)))
        self.parameters = parameters if parameters else {}

        mesh.update_default_vertex_attributes({'scalar_field': 0})

    def generate_paths(self):
        """ Generates isocontours. """
        start_domain, end_domain = min(self.scalar_field), max(self.scalar_field)
        step = (end_domain - start_domain) / (self.no_of_isocurves + 1)

        max_dist = get_param(self.parameters, key='vertical_layers_max_centroid_dist', defaults_type='layers')
        vertical_layers_manager = VerticalLayersManager(max_dist)

        # create paths + layers
        with progressbar.ProgressBar(max_value=self.no_of_isocurves) as bar:
            for i in range(0, self.no_of_isocurves + 1):
                for vkey, data in self.mesh.vertices(data=True):
                    if i == 0:
                        data['scalar_field'] = self.scalar_field[vkey] - 0.05 * step  # things can be tricky in the edge
                    else:
                        data['scalar_field'] = self.scalar_field[vkey] - i * step

                contours = ScalarFieldContours(self.mesh)
                contours.compute()
                contours.add_to_vertical_layers_manager(vertical_layers_manager)

                bar.update(i)  # advance progress bar

        self.layers = vertical_layers_manager.layers


if __name__ == "__main__":
    pass
