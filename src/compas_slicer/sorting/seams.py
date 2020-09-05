import logging

from compas.geometry import Point
from compas.geometry import distance_point_point

logger = logging.getLogger('logger')

__all__ = ['align_seams']


def align_seams(slicer, seam_orientation="next_path"):
    """Aligns the seams of a print

    Parameters
    ----------
    slicer : compas_slicer.slicers
        A compas_slicer.slicers instance
    seam_orientation : str
        Direction to orient the seams in.
        next_path = orients the seam to the next path
        origin       = orients the seam to the origin (0,0,0)
        x_axis       = orients the seam to the x_axis
        y_axis       = orients the seam to the y_axis
    """
    # TODO: Implement random seams 
    logger.info("Aligning seams to: %s" % seam_orientation)

    for path_collection in slicer.path_collections:
        for i, path in enumerate(path_collection.paths):
            if i < len(path_collection.paths) - 1:
                if seam_orientation == "next_path":
                    current_pt0 = path.points[0]
                elif seam_orientation == "origin":
                    current_pt0 = Point(0, 0, 0)
                elif seam_orientation == "x_axis":
                    current_pt0 = Point(2 ** 32, 0, 0)
                elif seam_orientation == "y_axis":
                    current_pt0 = Point(0, 2 ** 32, 0)

                # gets the points of the next path
                next_path_pts = path_collection.paths[i + 1].points

                # removes the last element of the list before shifting
                next_path_pts = next_path_pts[:-1]

                # computes distance between current_pt0 and the next path points
                next_path_distance = [distance_point_point(current_pt0, pt) for pt in next_path_pts]

                # gets the index of the closest point by looking for the minimum                    
                next_start_index = next_path_distance.index(min(next_path_distance))

                # gets the list of points for the next path, minus the last point
                next_path_list = path_collection.paths[i + 1].points[:-1]

                # shifts the list by the distance determined
                shift_list = next_path_list[next_start_index:] + next_path_list[:next_start_index]

                # adds the first point to the end to create a closed path and
                # adds the shifted point to the points
                path_collection.paths[i + 1].points = shift_list + [shift_list[0]]


if __name__ == "__main__":
    pass
