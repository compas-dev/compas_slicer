from compas_slicer.slicers import BaseSlicer

from compas_slicer.slicers.curved_slicing import find_desired_number_of_isocurves
import logging
from compas_slicer.slicers.curved_slicing import IsocurvesGenerator

logger = logging.getLogger('logger')

__all__ = ['CurvedSlicer']


class CurvedSlicer(BaseSlicer):
    """
    CurvedSlicer is....

    Attributes
    ----------
    mesh : compas.datastructures.Mesh
        Input mesh, it must be a triangular mesh (i.e. no quads or n-gons allowed)
    preprocessor :
    DATA_PATH :
    parameters :
    """

    def __init__(self, mesh, preprocessor, parameters, DATA_PATH):
        BaseSlicer.__init__(self, mesh)

        self.DATA_PATH = DATA_PATH
        self.parameters = parameters
        self.preprocessor = preprocessor

    def generate_paths(self):
        # --- generate paths
        n = find_desired_number_of_isocurves(self.preprocessor.target_LOW, self.preprocessor.target_HIGH,
                                             self.parameters['avg_layer_height'])
        isocurves_generator = IsocurvesGenerator(self.mesh, self.preprocessor.target_LOW,
                                                 self.preprocessor.target_HIGH, n)
        self.layers = isocurves_generator.segments


if __name__ == "__main__":
    pass
