from compas.geometry import distance_point_point
from compas_slicer.geometry import VerticalLayer
import compas_slicer.utilities as utils

import logging

logger = logging.getLogger('logger')

__all__ = ['sort_per_segment']


def sort_per_segment(slicer, max_layers_per_segment, threshold):
    """Sorts in vertical segments the contours that are stored in the horizontal layers.
    This is done by grouping the centroids of the paths based on proximity.

    Parameters
    ----------
    layers : list
        An instance of the compas_slicer.slicing.printpath.Layer class.
    d_threshold : float
        The maximum distance that the centroids of two successive paths can have to belong in the same group
        Recommended value, slightly bigger than the layer height
    max_layers_per_segment : int
        Maximum number of layers that a segment can consist of
        If None, then the segment has unlimited number of layers
    """
    logger.info("Sorting per segment")

    segments = [VerticalLayer(id=0)]  # segments that contain isocurves
    for layer in slicer.layers:
        for path in layer.paths:
            current_segment = None

            #  Find an eligible segment for contour (called current_segment)
            if len(segments[0].paths) == 0:  # first contour
                current_segment = segments[0]
            else:  # find the candidate segment for new isocurve
                contour_centroid = utils.get_average_point(path.points)
                other_centroids = get_segments_centroids_list(segments)
                candidate_segment = segments[get_closest_pt_index(contour_centroid, other_centroids)]
                if distance_point_point(candidate_segment.head_centroid, contour_centroid) < threshold:
                    if max_layers_per_segment:
                        if len(candidate_segment.paths) < max_layers_per_segment:
                            current_segment = candidate_segment
                    else:  # then no restriction in the number of layers
                        current_segment = candidate_segment

                if not current_segment:  # then create new segment
                    current_segment = VerticalLayer(id=segments[-1].id + 1)
                    segments.append(current_segment)

            #  Assign contour to current segment
            current_segment.append_(path)

    logger.info("Number of segments : %d" % len(segments))
    slicer.print_paths = segments


def get_closest_pt_index(pt, pts):
    distances = [distance_point_point(p, pt) for p in pts]
    min_index = distances.index(min(distances))
    return min_index


def get_segments_centroids_list(segments):
    head_centroids = []
    for segment in segments:
        head_centroids.append(segment.head_centroid)
    return head_centroids


if __name__ == "__main__":
    pass
