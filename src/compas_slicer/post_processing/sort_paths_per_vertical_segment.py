from compas.geometry import distance_point_point
from compas_slicer.geometry import VerticalLayer
import compas_slicer.utilities as utils
import numpy as np

import logging

logger = logging.getLogger('logger')

__all__ = ['sort_per_vertical_segment',
           'get_segments_centroids_list']


def sort_per_vertical_segment(slicer, dist_threshold=30.0, max_layers_per_segment=None, ):
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
        Maximum number of layers that a segment can consist of
        If None, then the segment has unlimited number of layers

    """
    logger.info("Sorting into Vertical Layers")

    vertical_segments = [VerticalLayer(id=0)]  # vertical_layers that contain isocurves
    for layer in slicer.layers:
        for path in layer.paths:
            current_segment = None

            #  Find an eligible segment for contour (called current_segment)
            if len(vertical_segments[0].paths) == 0:  # first contour
                current_segment = vertical_segments[0]
            else:  # find the candidate segment for new isocurve
                contour_centroid = list(np.average(np.array(path.points), axis=0))
                other_centroids = get_segments_centroids_list(vertical_segments)
                candidate_segment = vertical_segments[utils.get_closest_pt_index(contour_centroid, other_centroids)]
                if distance_point_point(candidate_segment.head_centroid, contour_centroid) < dist_threshold:
                    if max_layers_per_segment:
                        if len(candidate_segment.paths) < max_layers_per_segment:
                            current_segment = candidate_segment
                    else:  # then no restriction in the number of layers
                        current_segment = candidate_segment

                if not current_segment:  # then create new segment
                    current_segment = VerticalLayer(id=vertical_segments[-1].id + 1)
                    vertical_segments.append(current_segment)

            #  Assign contour to current segment
            current_segment.append_(path)

    logger.info("Number of vertical_layers: %d" % len(vertical_segments))
    slicer.layers = vertical_segments

    # Updates min_max_z_height attributes
    for vert_layer in slicer.layers:
        min_max_z = (vert_layer.paths[0].points[0][2], vert_layer.paths[len(vert_layer.paths)-1].points[0][2])
        vert_layer.min_max_z_height = min_max_z

def get_segments_centroids_list(segments):
    """ Returns a list with points that are the centroids of the heads of all vertical_layers_print_data. The head
    of a segment is its last path. """
    head_centroids = []
    for segment in segments:
        head_centroids.append(segment.head_centroid)
    return head_centroids


if __name__ == "__main__":
    pass
