import logging

from compas.geometry import Point
from compas.geometry import distance_point_point

logger = logging.getLogger('logger')

__all__ = ['align_seams']

def align_seams(slicer, seam_orientation="next_contour"):
    """Aligns the seams of a print

    Parameters
    ----------
    slicer : compas_slicer.slicers
        A compas_slicer.slicers instance
    seam_orientation : str
        Direction to orient the seams in.
        next_contour = orients the seam to the next contour
        origin       = orients the seam to the origin (0,0,0)
        x_axis       = orients the seam to the x_axis
        y_axis       = orients the seam to the y_axis
    """
    # TODO: Implement random seams 
    logger.info("Aligning seams to: %s" %seam_orientation)

    layers = slicer.print_paths
    for layer in layers:
        for i, contour in enumerate(layer.contours):
            if i < len(layer.contours)-1:
                if seam_orientation == "next_contour":
                    current_pt0 = contour.printpoints[0]
                elif seam_orientation == "origin":
                    current_pt0 = Point(0, 0, 0)
                elif seam_orientation == "x_axis":
                    current_pt0 = Point(2**32, 0, 0)
                elif seam_orientation == "y_axis":
                    current_pt0 = Point(0, 2**32, 0)
                
                # gets the points of the next contour
                next_contour_pts = layer.contours[i+1].printpoints
                
                # removes the last element of the list before shifting
                next_contour_pts = next_contour_pts[:-1]

                # computes distance between current_pt0 and the next contour points
                next_contour_distance = [distance_point_point(current_pt0, pt) for pt in next_contour_pts]

                # gets the index of the closest point by looking for the minimum                    
                next_start_index = next_contour_distance.index(min(next_contour_distance))

                # gets the list of points for the next contour, minus the last point
                next_contour_list = layer.contours[i+1].printpoints[:-1]
                
                # shifts the list by the distance determined
                shift_list = next_contour_list[next_start_index:] + next_contour_list[:next_start_index]

                # adds the first point to the end to create a closed contour and 
                # adds the shifted point to the printpoints
                layer.contours[i+1].printpoints = shift_list + [shift_list[0]]

if __name__ == "__main__":
    pass
