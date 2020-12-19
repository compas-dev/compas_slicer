from compas_slicer.slicers import BaseSlicer

from compas_slicer.slicers.curved_slicing import find_desired_number_of_isocurves
import logging
from compas_slicer.slicers.curved_slicing import IsocurvesGenerator
from compas_slicer.parameters import get_param

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

    def __init__(self, mesh, preprocessor=None, parameters=None):
        BaseSlicer.__init__(self, mesh)
        if preprocessor:
            # make sure the mesh of the preprocessor and the mesh of the slicer match
            assert len(list(mesh.vertices())) == len(list(preprocessor.mesh.vertices()))

        self.parameters = parameters
        self.preprocessor = preprocessor
        self.n_multiplier = 1.0

    def generate_paths(self):
        """ Generates curved paths-polylines. """
        assert self.preprocessor, 'You need to provide a pre-prosessor in order to generate paths.'
        assert self.parameters, 'You need to provide a parameters dict in order to generate paths.'

        avg_layer_height = get_param(self.parameters, key='avg_layer_height', defaults_type='curved_slicing')
        n = find_desired_number_of_isocurves(self.preprocessor.target_LOW, self.preprocessor.target_HIGH,
                                             avg_layer_height)
        logger.info('%d paths will be generated' % n)

        isocurves_generator = IsocurvesGenerator(self.mesh, self.preprocessor.target_LOW,
                                                 self.preprocessor.target_HIGH, n * self.n_multiplier)
        self.layers = isocurves_generator.segments


if __name__ == "__main__":
    pass
