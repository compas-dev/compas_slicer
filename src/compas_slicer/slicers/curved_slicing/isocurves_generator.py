import numpy as np
import compas_slicer.utilities as utils
from compas_slicer.geometry import VerticalLayer, Path
import logging
import progressbar
from compas_slicer.pre_processing import assign_distance_to_mesh_vertices
from compas_slicer.pre_processing import GeodesicsZeroCrossingContours
from compas_slicer.post_processing.sort_paths_per_vertical_segment import get_segments_centroids_list

logger = logging.getLogger('logger')

__all__ = ['IsocurvesGenerator']


class IsocurvesGenerator:
    """
    Generates isocurves that lie on the input mesh and interpolate the targets (target_LOW, target_HIGH)

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    target_LOW: :class: 'compas_slicer.slicing.curved_slicing.CompoundTarget'
    target_HIGH: :class: 'compas_slicer.slicing.curved_slicing.CompoundTarget'
    number_of_curves : int
    """

    def __init__(self, mesh, target_LOW, target_HIGH, number_of_curves):
        logging.info("Isocurves Generator...")
        self.mesh = mesh  # compas mesh
        self.target_LOW = target_LOW
        self.target_HIGH = target_HIGH

        #  main
        self.segments = [VerticalLayer(id=0)]  # segments that contain isocurves (compas_slicer.Path)
        weights_list = get_weights_list(number_of_curves)
        weights_list.pop(0)  # remove first curves that is on 0 (lies on BaseBoundary)
        self.create_isocurves(weights_list)

    def create_isocurves(self, weights_list):
        """
        Creates one isocurve for each weight

        Parameters
        ----------
        weights_list: list, float, the weights in ascending order.
        """
        with progressbar.ProgressBar(max_value=len(weights_list)) as bar:
            for i, weight in enumerate(weights_list):
                assign_distance_to_mesh_vertices(self.mesh, weight, self.target_LOW, self.target_HIGH)
                zero_contours = GeodesicsZeroCrossingContours(self.mesh)
                zero_contours.compute()

                for j, key in enumerate(zero_contours.sorted_point_clusters):
                    pts = zero_contours.sorted_point_clusters[key]

                    if len(pts) > 4:  # discard curves that are too small

                        #  --- Assign resulting clusters to the correct segment: current segment
                        if (i == 0 and j == 0) or len(self.segments[0].paths) == 0:
                            current_segment = self.segments[0]
                        else:  # find the candidate segment for new isocurve
                            centroid = np.mean(np.array(pts), axis=0)
                            other_centroids = get_segments_centroids_list(self.segments)
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


def get_weights_list(number_of_curves):
    """ Returns a list of #number_of_curves floats from 0.001 to 0.997. """
    t_list = [0.001]
    a = list(np.arange(number_of_curves + 1) / (number_of_curves + 1))
    a.pop(0)
    t_list.extend(a)
    t_list.append(0.997)
    return t_list


if __name__ == "__main__":
    pass
