import numpy as np
from compas.geometry import Vector, add_vectors, scale_vector
import compas_slicer.utilities as utils
from compas_slicer.geometry import VerticalLayer, Path
import logging
from compas_slicer.slicers.curved_slicing.get_weighted_distance import get_weighted_distance
from progress.bar import Bar
from compas_slicer.slicers.slice_utilities import ZeroCrossingContours

logger = logging.getLogger('logger')

__all__ = ['IsocurvesGenerator']


class IsocurvesGenerator:
    def __init__(self, mesh_, target_LOW, target_HIGH, number_of_curves):
        logging.info("Isocurves Generator...")
        self.mesh = mesh_  # compas mesh
        self.target_LOW = target_LOW
        self.target_HIGH = target_HIGH

        #  main
        self.segments = [VerticalLayer(id=0)]  # segments that contain isocurves (compas_slicer.Path)
        t_list = get_t_list(number_of_curves)
        t_list.pop(0)  # remove first curves that is on 0 (lies on BaseBoundary)
        self.create_isocurves(t_list)

    #  --- main

    def create_isocurves(self, t_list):
        progress_bar = Bar(' Isocurves Generation', max=len(t_list),
                           suffix='Layer %(index)i/%(max)i - %(percent)d%%')
        for i, t in enumerate(t_list):
            self.assign_distance_attribute_to_mesh_vertices(t)
            zero_contours = GeodesicsZeroCrossingContour(self.mesh)
            zero_contours.compute()

            for j, key in enumerate(zero_contours.sorted_point_clusters):
                pts = zero_contours.sorted_point_clusters[key]

                if len(pts) > 4:  # discard curves that are too small

                    #  --- Assign resulting clusters to the correct segment: current segment
                    if (i == 0 and j == 0) or len(self.segments[0].paths) == 0:
                        current_segment = self.segments[0]
                    else:  # find the candidate segment for new isocurve
                        centroid = np.mean(np.array(pts), axis=0)
                        other_centroids = self.get_segments_centroids_list()
                        candidate_segment = self.segments[utils.get_closest_pt_index(centroid, other_centroids)]
                        threshold_max_centroid_dist = 25
                        if np.linalg.norm(candidate_segment.head_centroid - centroid) < threshold_max_centroid_dist:
                            current_segment = candidate_segment
                        else:  # then create new segment
                            current_segment = VerticalLayer(id=self.segments[-1].id + 1)
                            self.segments.append(current_segment)

                    # --- Create paths
                    isocurve = Path(pts, is_closed=zero_contours.closed_paths_booleans[key])
                    current_segment.append_(isocurve)
            # advance progress bar
            progress_bar.next()
        # finish progress bar
        progress_bar.finish()

    def assign_distance_attribute_to_mesh_vertices(self, weight):
        if self.target_LOW and self.target_HIGH:
            for vkey in self.mesh.vertices():
                d = get_weighted_distance(vkey, weight, self.target_LOW, self.target_HIGH)
                self.mesh.vertex[vkey]["distance"] = d
        else:
            assert self.target_LOW, 'You need to provide one target at least.'
            offset = weight * max(self.target_LOW.all_distances())
            for vkey in self.mesh.vertices():
                self.mesh.vertex[vkey]["distance"] = self.target_LOW.distance(vkey) - offset

    def get_segments_centroids_list(self):
        head_centroids = []
        for segment in self.segments:
            head_centroids.append(segment.head_centroid)
        return head_centroids


#################################
#  Additional post_processing

class GeodesicsZeroCrossingContour(ZeroCrossingContours):
    def __init__(self, mesh):
        ZeroCrossingContours.__init__(self, mesh)  # initialize from parent class

    def edge_is_intersected(self, u, v):
        d1 = self.mesh.vertex[u]['distance']
        d2 = self.mesh.vertex[v]['distance']
        if (d1 > 0 and d2 > 0) or (d1 < 0 and d2 < 0):
            return False
        else:
            return True

    def find_zero_crossing_point(self, u, v):
        dist_a, dist_b = self.mesh.vertex[u]['distance'], self.mesh.vertex[v]['distance']
        if abs(dist_a) + abs(dist_b) > 0:
            v_coords_a, v_coords_b = self.mesh.vertex_coordinates(u), self.mesh.vertex_coordinates(v)
            vec = Vector.from_start_end(v_coords_a, v_coords_b)
            vec = scale_vector(vec, abs(dist_a) / (abs(dist_a) + abs(dist_b)))
            pt = add_vectors(v_coords_a, vec)
            return pt


def get_t_list(number_of_curves):
    t_list = [0.001]  # [0.001]
    a = list(np.arange(number_of_curves + 1) / (number_of_curves + 1))
    a.pop(0)
    t_list.extend(a)
    t_list.append(0.997)
    return t_list
