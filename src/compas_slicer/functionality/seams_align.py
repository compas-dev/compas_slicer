import logging

from compas.geometry import Point
from compas.geometry import distance_point_point

logger = logging.getLogger('logger')

__all__ = ['seams_align']


def seams_align(slicer, seam_orientation="next_path"):
    """Aligns the seams (start- and endpoint) of a print.

    Parameters
    ----------
    slicer : compas_slicer.slicers
        A compas_slicer.slicers instance
    seam_orientation : str
        Direction to orient the seams in.
        next_path   = orients the seam to the next path
        origin      = orients the seam to the origin (0,0,0)
        x_axis      = orients the seam to the x_axis
        y_axis      = orients the seam to the y_axis
    """
    # TODO: Implement random seams 
    logger.info("Aligning seams to: %s" % seam_orientation)

    for i, layer in enumerate(slicer.layers):
        for j, path in enumerate(layer.paths):            
            if seam_orientation == "next_path":
                current_pt0 = path.points[0]
            elif seam_orientation == "origin":
                current_pt0 = Point(0, 0, 0)
            elif seam_orientation == "x_axis":
                current_pt0 = Point(2 ** 32, 0, 0)
            elif seam_orientation == "y_axis":
                current_pt0 = Point(0, 2 ** 32, 0)
                
            if len(layer.paths) == 1:
                # if there is only one contour per layer:
                # take the next layer as the next path
                if i < len(slicer.layers) - 1:
                    if seam_orientation == "next_path":
                        next_path_pts = slicer.layers[i+1].paths[0].points
                    else:
                        next_path_pts = slicer.layers[i].paths[0].points
                else:
                    if seam_orientation != "next_path":
                        next_path_pts = slicer.layers[i].paths[0].points
            else:
                # if there are multiple contours per layer
                # gets the points of the next path
                if j < len(layer.paths) - 1:
                    next_path_pts = layer.paths[j + 1].points

            # removes the last element of the list before shifting
            next_path_pts = next_path_pts[:-1]

            # computes distance between current_pt0 and the next path points
            next_path_distance = [distance_point_point(current_pt0, pt) for pt in next_path_pts]

            # gets the index of the closest point by looking for the minimum                    
            next_start_index = next_path_distance.index(min(next_path_distance))

            # gets the list of points for the next path, minus the last point
            next_path_list = next_path_pts[:-1]

            # shifts the list by the distance determined
            shift_list = next_path_list[next_start_index:] + next_path_list[:next_start_index]

            # adds the first point to the end to create a closed path and
            # adds the shifted point to the points
            if len(layer.paths) ==  1:
                if i < len(slicer.layers) - 1:
                    if seam_orientation == "next_path":
                        slicer.layers[i+1].paths[0].points = shift_list + [shift_list[0]]
                    else:
                        slicer.layers[i].paths[0].points = shift_list + [shift_list[0]]
                else:
                    if seam_orientation != "next_path":
                        slicer.layers[i].paths[0].points = shift_list + [shift_list[0]]
                    
            else:
                if j < len(layer.paths) - 1:
                    layer.paths[j + 1].points = shift_list + [shift_list[0]]
            

if __name__ == "__main__":
    pass
