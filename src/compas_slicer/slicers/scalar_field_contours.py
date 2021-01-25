import numpy as np
from compas_slicer.slicers import BaseSlicer
import logging
from compas_slicer.pre_processing import CurvedZeroCrossingContours
from compas_slicer.geometry import VerticalLayer, Path

logger = logging.getLogger('logger')

__all__ = ['ScalarFieldContours']


class ScalarFieldContours(BaseSlicer):
    def __init__(self, mesh, scalar_field, no_of_isocurves):
        BaseSlicer.__init__(self, mesh)
        self.no_of_isocurves = no_of_isocurves
        logger.info('ScalarFieldContours')
        self.scalar_field = list(np.array(scalar_field) - np.max(np.array(scalar_field)))
        mesh.update_default_vertex_attributes({'scalar_field': 0})

    def generate_paths(self):
        start_domain, end_domain = min(self.scalar_field), max(self.scalar_field)
        step = (end_domain - start_domain) / (self.no_of_isocurves + 1)

        paths = []
        for i in range(1, self.no_of_isocurves + 1):
            for vkey, data in self.mesh.vertices(data=True):
                data['scalar_field'] = self.scalar_field[vkey] + i * step

            zero_contours = CurvedZeroCrossingContours(self.mesh)
            zero_contours.compute()

            for key in zero_contours.sorted_point_clusters:
                pts = zero_contours.sorted_point_clusters[key]
                paths.append(Path(pts, is_closed=zero_contours.closed_paths_booleans[key]))

        self.layers.append(VerticalLayer(paths=paths))
