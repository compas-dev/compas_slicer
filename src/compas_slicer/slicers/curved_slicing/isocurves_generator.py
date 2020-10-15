import numpy as np
import math
import igl
from compas_slicer.geometry import VerticalLayer
import logging
from progress.bar import Bar
import networkx as nx
from compas_slicer.slicers.slice_utilities import create_graph_from_mesh_vkeys

logger = logging.getLogger('logger')

__all__ = ['IsocurvesGenerator']


class IsocurvesGenerator:
    def __init__(self, mesh_, target_LOW, target_HIGH, number_of_curves):
        logging.info("Isocurves Generator...")
        self.mesh = mesh_  # compas mesh
        self.target_LOW = target_LOW
        self.target_HIGH = target_HIGH

        ### main
        self.segments = [VerticalLayer(id=0)]  # segments that contain isocurves
        t_list = get_t_list(number_of_curves)
        self.create_isocurves(t_list)

        # ### post processing
        # self.orient_isocurves_and_align_seams()
        #
        # total_number_of_points = 0
        # for segment in self.segments:
        #     total_number_of_points += segment.total_number_of_points()
        # logger.info("Created %d segments with %d total number of points" % (len(self.segments), total_number_of_points))

    ### --- main


    def create_isocurves(self, t_list):
        for i, t in enumerate(t_list):
            logger.info("--- %d : Creating isocurve(s) on level %.3f" % (i, t))
    
            t_clustering = EdgeClustering(self.mesh, t, self.target_LOW, self.target_HIGH)
            t_clustering.generate_edge_clusters_method(sort_clusters=True)
            t_clustering.generate_point_clusters_method()

            for j, cluster_key in enumerate(t_clustering.point_clusters):
                pts = t_clustering.point_clusters[cluster_key]

                if len(pts) > 4:  # discard curves that are too small

                    ### --- Assign resulting clusters to the correct segment: current segment
                    if (i == 0 and j == 0) or len(self.segments[0].isocurves) == 0:
                        current_segment = self.segments[0]
                    else:  # find the candidate segment for new isocurve
                        centroid = np.mean(np.array(pts), axis=0)
                        other_centroids = self.get_segments_centroids_list()
                        candidate_segment = self.segments[utils.get_closest_pt_index(centroid, other_centroids)]
                        if np.linalg.norm(candidate_segment.head_centroid - centroid) < get_param(
                                'segments_max_centroid_dist'):
                            current_segment = candidate_segment
                        else:  # then create new segment
                            current_segment = Segment(id=self.segments[-1].id + 1)
                            self.segments.append(current_segment)

                    ### --- Create isocurves
                    if len(current_segment.isocurves) == 0:
                        isocurve = Isocurve(pts, reference_isocurve=None)
                    else:
                        isocurve = Isocurve(pts, reference_isocurve=current_segment.isocurves[-1])

                    if isocurve.is_valid:
                        current_segment.append_(isocurve)

 #########################
 #  Additional utils

def get_t_list(number_of_curves):
    t_list = [0.001]  # [0.001]
    a = list(np.arange(number_of_curves + 1) / (number_of_curves + 1))
    a.pop(0)
    t_list.extend(a)
    t_list.append(0.997)
    return t_list