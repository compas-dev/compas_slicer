import numpy as np
from compas_slicer.slicers import BaseSlicer
import logging
import progressbar
from compas_slicer.parameters import get_param
from compas_slicer.pre_processing import assign_interpolation_distance_to_mesh_vertices
from compas_slicer.slicers.slice_utilities import ScalarFieldContours
from compas_slicer.geometry import VerticalLayersManager

logger = logging.getLogger('logger')

__all__ = ['InterpolationSlicer']


class InterpolationSlicer(BaseSlicer):
    """
    Generates non-planar contours that interpolate user-defined boundaries.

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
        Input mesh, it must be a triangular mesh (i.e. no quads or n-gons allowed)
        Note that the topology of the mesh matters, irregular tesselation can lead to undesired results.
        We recommend to 1)re-topologize, 2) triangulate, and 3) weld your mesh in advance.
    preprocessor: :class: 'compas_slicer.pre_processing.InterpolationSlicingPreprocessor'
    parameters: dict
    """

    def __init__(self, mesh, preprocessor=None, parameters=None):
        logger.info('InterpolationSlicer')
        BaseSlicer.__init__(self, mesh)

        if preprocessor:  # make sure the mesh of the preprocessor and the mesh of the slicer match
            assert len(list(mesh.vertices())) == len(list(preprocessor.mesh.vertices()))

        self.parameters = parameters if parameters else {}
        self.preprocessor = preprocessor
        self.n_multiplier = 1.0

    def generate_paths(self):
        """ Generates curved paths. """
        assert self.preprocessor, 'You need to provide a pre-processor in order to generate paths.'

        avg_layer_height = get_param(self.parameters, key='avg_layer_height', defaults_type='layers')
        n = find_no_of_isocurves(self.preprocessor.target_LOW, self.preprocessor.target_HIGH, avg_layer_height)
        params_list = get_interpolation_parameters_list(n)
        logger.info('%d paths will be generated' % n)

        vertical_layers_manager = VerticalLayersManager(avg_layer_height)

        # create paths + layers
        with progressbar.ProgressBar(max_value=len(params_list)) as bar:
            for i, param in enumerate(params_list):
                assign_interpolation_distance_to_mesh_vertices(self.mesh, param, self.preprocessor.target_LOW,
                                                               self.preprocessor.target_HIGH)
                contours = ScalarFieldContours(self.mesh)
                contours.compute()
                contours.add_to_vertical_layers_manager(vertical_layers_manager)

                bar.update(i)  # advance progress bar

        self.layers = vertical_layers_manager.layers


def find_no_of_isocurves(target_0, target_1, avg_layer_height=1.1):
    """ Returns the average number of isocurves that can cover the get_distance from target_0 to target_1. """
    avg_ds0 = target_0.get_avg_distances_from_other_target(target_1)
    avg_ds1 = target_1.get_avg_distances_from_other_target(target_0)
    number_of_curves = ((avg_ds0 + avg_ds1) * 0.5) / avg_layer_height
    return max(1, int(number_of_curves))


def get_interpolation_parameters_list(number_of_curves):
    """ Returns a list of #number_of_curves floats from 0.001 to 0.997. """
    # t_list = [0.001]
    t_list = []
    a = list(np.arange(number_of_curves + 1) / (number_of_curves + 1))
    a.pop(0)
    t_list.extend(a)
    t_list.append(0.997)
    return t_list


if __name__ == "__main__":
    pass
