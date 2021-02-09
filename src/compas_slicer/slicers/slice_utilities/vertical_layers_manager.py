import numpy as np
import logging
from compas_slicer.geometry import VerticalLayer, Path
import compas_slicer.utilities as utils

logger = logging.getLogger('logger')

__all__ = ['VerticalLayersManager']


class VerticalLayersManager:
    """
    Creates empty vertical layers and assigns to the input paths to the fitting vertical layer using the add() function.
    The criterion for grouping paths to VerticalLayers is based on the proximity of the centroids of the paths.
    If the input paths don't fit in any vertical layer, then new vertical layer is created with that path.

    Attributes
    ----------
    threshold_max_centroid_dist:
        float. The maximum get_distance that the centroids of two successive paths can have to belong in the same
        VerticalLayer.
    max_paths_per_layer: int
        Maximum number of layers that a vertical layer can consist of.
        If None, then the vertical layer has an unlimited number of layers.
    """

    def __init__(self, threshold_max_centroid_dist=15.0, max_paths_per_layer=None):
        self.layers = [VerticalLayer(id=0)]  # vertical_layers_print_data that contain isocurves (compas_slicer.Path)
        self.threshold_max_centroid_dist = threshold_max_centroid_dist
        self.max_paths_per_layer = max_paths_per_layer

    def add(self, path):
        selected_layer = None

        #  Find an eligible layer for path (called selected_layer)
        if len(self.layers[0].paths) == 0:  # first path goes to first layer
            selected_layer = self.layers[0]

        else:  # find the candidate segment for new isocurve
            centroid = np.mean(np.array(path.points), axis=0)
            other_centroids = get_vertical_layers_centroids_list(self.layers)
            candidate_layer = self.layers[utils.get_closest_pt_index(centroid, other_centroids)]

            if np.linalg.norm(candidate_layer.head_centroid - centroid) < self.threshold_max_centroid_dist:
                if self.max_paths_per_layer:
                    if len(candidate_layer.paths) < self.max_paths_per_layer:
                        selected_layer = candidate_layer
                else:
                    selected_layer = candidate_layer

            if not selected_layer:  # then create new layer
                selected_layer = VerticalLayer(id=self.layers[-1].id + 1)
                self.layers.append(selected_layer)

        selected_layer.append_(path)


def get_vertical_layers_centroids_list(vert_layers):
    """ Returns a list with points that are the centroids of the heads of all vertical_layers_print_data. The head
    of a vertical_layer is its last path. """
    head_centroids = []
    for vert_layer in vert_layers:
        head_centroids.append(vert_layer.head_centroid)
    return head_centroids
