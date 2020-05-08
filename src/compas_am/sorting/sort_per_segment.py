from compas.geometry import distance_point_point
from compas_am.slicing.printpath import Segment
import numpy as np

import logging
logger = logging.getLogger('logger')

def sort_per_segment(layers, d_threshold):

    segments = [Segment(id = 0)] #segments that contain isocurves
    for layer in layers: 
        for contour in layer.contours:
            pts = contour.points

            ## Find an eligible segment for contour (called current_segment)
            if len(segments[0].contours) == 0: #first contour
                current_segment = segments[0]  
            else: # find the candidate segment for new isocurve
                contour_centroid = np.mean(np.array(pts), axis=0)
                other_centroids = get_segments_centroids_list(segments)
                candidate_segment = segments[get_closest_pt_index(contour_centroid, other_centroids)]    
                if np.linalg.norm(candidate_segment.head_centroid - contour_centroid) < d_threshold:
                    current_segment = candidate_segment
                else: #then create new segment
                    current_segment = Segment(id = segments[-1].id + 1)
                    segments.append(current_segment)

            ## Assign contour to current segment
            current_segment.append_(contour)

        ##TODO: 
        # if layer.infill_paths: ...
        # if layer.support_paths: ...

    logger.info("Number of segments : %d"%len(segments))
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

