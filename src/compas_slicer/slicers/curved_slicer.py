from compas_slicer.slicers import BaseSlicer

from compas_slicer.slicers.curved_slicing import find_desired_number_of_isocurves
import logging
from compas_slicer.slicers.curved_slicing import IsocurvesGenerator
import compas_slicer.utilities as utils
logger = logging.getLogger('logger')

__all__ = ['CurvedSlicer']


class CurvedSlicer(BaseSlicer):
    """
    Generates non-planar contours that interpolate user-defined boundaries.

    Attributes
    ----------
    mesh : :class: 'compas.datastructures.Mesh'
        Input mesh, it must be a triangular mesh (i.e. no quads or n-gons allowed)
        Note that the topology of the mesh matters, irregular tesselation can lead to undesired results.
        WE recommend to 1)retopologize, 2) triangulate, and 3) weld your mesh in advance.
    preprocessor : :class: 'compas_slicer.pre_processing.CurvedSlicingPreprocessor'
    parameters : dict
    """

    def __init__(self, mesh, preprocessor, parameters):
        BaseSlicer.__init__(self, mesh)
        assert len(list(mesh.vertices())) == len(list(preprocessor.mesh.vertices()))

        self.parameters = parameters
        self.preprocessor = preprocessor
        self.n_multiplier = 1.0

    def generate_paths(self):
        """ Generates curved paths-polylines. """
        avg_layer_height = utils.get_param(self.parameters, 'avg_layer_height', default_value=5.0)
        n = find_desired_number_of_isocurves(self.preprocessor.target_LOW, self.preprocessor.target_HIGH,
                                             avg_layer_height)
        logger.info('%d paths will be generated' % n)

        isocurves_generator = IsocurvesGenerator(self.mesh, self.preprocessor.target_LOW,
                                                 self.preprocessor.target_HIGH, n * self.n_multiplier)
        self.layers = isocurves_generator.segments


if __name__ == "__main__":
    pass
