from compas.geometry import distance_point_point
from compas_slicer.geometry import VerticalLayer
import compas_slicer.utilities as utils
import numpy as np

import logging

logger = logging.getLogger('logger')

__all__ = ['sort_into_vertical_layers',
           'get_vertical_layers_centroids_list']


def sort_into_vertical_layers(slicer, dist_threshold=30.0, max_paths_per_vertical_layer=None):
    """Sorts the paths from horizontal layers into Vertical Layers.

    Vertical Layers are layers at different heights that are grouped together by proximity
    of their center points. Can be useful for reducing travel time in a robotic printing
    process.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    dist_threshold: float
        The maximum get_distance that the centroids of two successive paths can have to belong in the same group
        Recommended value, slightly bigger than the layer height
    max_layers_per_segment: int
        Maximum number of layers that a vertical layer can consist of
        If None, then the vertical layer has an unlimited number of layers

    """
    logger.info("Sorting into Vertical Layers")

    vertical_layers = [VerticalLayer(id=0)]  # vertical_layers that contain isocurves
    for layer in slicer.layers:
        for path in layer.paths:
            current_segment = None

            #  Find an eligible segment for contour (called current_segment)
            if len(vertical_layers[0].paths) == 0:  # first contour
                current_segment = vertical_layers[0]
            else:  # find the candidate segment for new isocurve
                contour_centroid = list(np.average(np.array(path.points), axis=0))
                other_centroids = get_vertical_layers_centroids_list(vertical_layers)
                candidate_segment = vertical_layers[utils.get_closest_pt_index(contour_centroid, other_centroids)]
                if distance_point_point(candidate_segment.head_centroid, contour_centroid) < dist_threshold:
                    if max_paths_per_vertical_layer:
                        if len(candidate_segment.paths) < max_paths_per_vertical_layer:
                            current_segment = candidate_segment
                    else:  # then no restriction in the number of layers
                        current_segment = candidate_segment

                if not current_segment:  # then create new segment
                    current_segment = VerticalLayer(id=vertical_layers[-1].id + 1)
                    vertical_layers.append(current_segment)

            #  Assign contour to current segment
            current_segment.append_(path)

    logger.info("Number of vertical_layers: %d" % len(vertical_layers))
    slicer.layers = vertical_layers


def get_vertical_layers_centroids_list(vert_layers):
    """ Returns a list with points that are the centroids of the heads of all vertical_layers_print_data. The head
    of a vertical_layer is its last path. """
    head_centroids = []
    for vert_layer in vert_layers:
        head_centroids.append(vert_layer.head_centroid)
    return head_centroids


if __name__ == "__main__":
    pass
