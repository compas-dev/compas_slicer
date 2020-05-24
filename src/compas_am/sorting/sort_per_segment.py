from compas.geometry import distance_point_point
from compas_am.print_path import Segment
import numpy as np

import logging

logger = logging.getLogger('logger')


def sort_per_segment(layers, max_layers_per_segment, d_threshold):
    """Sorts in vertical segments the contours that are stored in the horizontal layers.
    This is done by grouping the centroids of the paths based on proximity. 

    Parameters
    ----------
    layers : list
        An instance of the compas_am.slicing.printpath.Layer class. 
    d_threshold : float
        The maximum distance that the centroids of two successive paths can have to belong in the same group
        Recommended value, slightly bigger than the layer height
    max_layers_per_segment : int
        Maximum number of layers that a segment can consist of
        If None, then the segment has unlimited number of layers
    

    """

    segments = [Segment(id=0)]  # segments that contain isocurves
    for layer in layers:
        for contour in layer.contours:
            current_segment = None

            ## Find an eligible segment for contour (called current_segment)
            if len(segments[0].contours) == 0:  # first contour
                current_segment = segments[0]
            else:  # find the candidate segment for new isocurve
                contour_centroid = np.mean(np.array([point.pt for point in contour.points]), axis=0)
                other_centroids = get_segments_centroids_list(segments)
                candidate_segment = segments[get_closest_pt_index(contour_centroid, other_centroids)]
                if np.linalg.norm(candidate_segment.head_centroid - contour_centroid) < d_threshold:
                    if max_layers_per_segment:
                        if len(candidate_segment.contours) < max_layers_per_segment:
                            current_segment = candidate_segment
                    else:  # then no restriction in the number of layers
                        current_segment = candidate_segment

                if not current_segment:  # then create new segment
                    current_segment = Segment(id=segments[-1].id + 1)
                    segments.append(current_segment)

            ## Assign contour to current segment
            current_segment.append_(contour)

        ##TODO: 
        # if layer.infill_paths: ...
        # if layer.support_paths: ...

    logger.info("Number of segments : %d" % len(segments))
    return segments


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
