import numpy as np
import compas_slicer.utilities as utils
from compas_slicer.geometry import VerticalLayer, Path
import logging
import compas_slicer
import progressbar
from compas_slicer.slicers import assign_distance_to_mesh_vertices

logger = logging.getLogger('logger')

__all__ = ['IsocurvesGenerator']


class IsocurvesGenerator:
    """
    IsocurvesGenerator is a class that generates isocurves that lie on the input
    mesh and interpolate the targets (target_LOW, target_HIGH)

    Attributes
    ----------
    mesh_ : compas.datastructures.Mesh
    target_LOW : compas_slicer.slicing.curved_slicing.CompoundTarget
    target_HIGH : compas_slicer.slicing.curved_slicing.CompoundTarget
    number_of_curves : int
    """
    def __init__(self, mesh, target_LOW, target_HIGH, number_of_curves):
        logging.info("Isocurves Generator...")
        self.mesh = mesh  # compas mesh
        self.target_LOW = target_LOW
        self.target_HIGH = target_HIGH

        #  main
        self.segments = [VerticalLayer(id=0)]  # segments that contain isocurves (compas_slicer.Path)
        t_list = get_t_list(number_of_curves)
        t_list.pop(0)  # remove first curves that is on 0 (lies on BaseBoundary)
        self.create_isocurves(t_list)

    #  --- main

    def create_isocurves(self, t_list):
        with progressbar.ProgressBar(max_value=len(t_list)) as bar:
            for i, t in enumerate(t_list):
                assign_distance_to_mesh_vertices(self.mesh, t, self.target_LOW, self.target_HIGH)
                zero_contours = compas_slicer.slicers.GeodesicsZeroCrossingContours(self.mesh)
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
                            threshold_max_centroid_dist = 15
                            if np.linalg.norm(candidate_segment.head_centroid - centroid) < threshold_max_centroid_dist:
                                current_segment = candidate_segment
                            else:  # then create new segment
                                current_segment = VerticalLayer(id=self.segments[-1].id + 1)
                                self.segments.append(current_segment)

                        # --- Create paths
                        isocurve = Path(pts, is_closed=zero_contours.closed_paths_booleans[key])
                        current_segment.append_(isocurve)
                # advance progress bar
                bar.update(i)

    def get_segments_centroids_list(self):
        head_centroids = []
        for segment in self.segments:
            head_centroids.append(segment.head_centroid)
        return head_centroids


#################################
#  Additional functionality

def get_t_list(number_of_curves):
    t_list = [0.001]  # [0.001]
    a = list(np.arange(number_of_curves + 1) / (number_of_curves + 1))
    a.pop(0)
    t_list.extend(a)
    t_list.append(0.997)
    return t_list
