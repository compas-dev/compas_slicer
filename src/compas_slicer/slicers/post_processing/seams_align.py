import logging

from compas.geometry import Point
from compas.geometry import distance_point_point

logger = logging.getLogger('logger')

__all__ = ['seams_align']


def seams_align(slicer, align_with="next_path"):
    """Aligns the seams (start- and endpoint) of a print.

    Parameters
    ----------
    slicer : compas_slicer.slicers
        A compas_slicer.slicers instance
    align_with : str or compas.geometry.Point
        Direction to orient the seams in.
        next_path    = orients the seam to the next path
        origin       = orients the seam to the origin (0,0,0)
        x_axis       = orients the seam to the x_axis
        y_axis       = orients the seam to the y_axis
        Point(x,y,z) = orients the seam according to the given point
    """
    #  TODO: Implement random seams
    logger.info("Aligning seams to: %s" % align_with)

    for i, layer in enumerate(slicer.layers):
        for j, path in enumerate(layer.paths):

            align_seams_for_current_path = path.is_closed  # should not happen if path is open

            if align_seams_for_current_path:
                #  get the points of the current layer and path
                path_to_change = slicer.layers[i].paths[j].points

                if align_with == "next_path":
                    pt_to_align_with = None  # make sure aligning point is cleared

                    #  determines the correct point to align the current layer with

                    if len(layer.paths) == 1 and i == 0:
                        #  if ONE PATH and FIRST LAYER
                        #  >>> align with second layer
                        pt_to_align_with = slicer.layers[i + 1].paths[0].points[0]
                    if len(layer.paths) == 1 and i != 0:
                        #  if ONE PATH and NOT FIRST LAYER
                        #  >>> align with previous layer
                        pt_to_align_with = slicer.layers[i - 1].paths[0].points[0]
                    if len(layer.paths) != 1 and i == 0 and j == 0:
                        #  if MULTIPLE PATHS and FIRST LAYER and FIRST PATH
                        #  >>> align with second path of first layer
                        pt_to_align_with = slicer.layers[i].paths[i + 1].points[0]
                    if len(layer.paths) != 1 and j != 0:
                        #  if MULTIPLE PATHS and NOT FIRST PATH
                        #  >>> align with previous path
                        pt_to_align_with = slicer.layers[i].paths[j - 1].points[0]
                    if len(layer.paths) != 1 and i != 0 and j == 0:
                        #  if MULTIPLE PATHS and NOT FIRST LAYER and FIRST PATH
                        #  >>> align with first path of previous layer
                        pt_to_align_with = slicer.layers[i - 1].paths[j].points[0]

                elif align_with == "origin":
                    pt_to_align_with = Point(0, 0, 0)
                elif align_with == "x_axis":
                    pt_to_align_with = Point(2 ** 32, 0, 0)
                elif align_with == "y_axis":
                    pt_to_align_with = Point(0, 2 ** 32, 0)
                elif isinstance(align_with, Point):
                    pt_to_align_with = align_with
                else:
                    raise NameError("Unknown align_with : " + str(align_with))

                #  computes distance between pt_to_align_with and the current path points
                distance_current_pt_align_pt = [distance_point_point(pt_to_align_with, pt) for pt in path_to_change]
                #  gets the index of the closest point by looking for the minimum
                new_start_index = distance_current_pt_align_pt.index(min(distance_current_pt_align_pt))
                #  shifts the list by the distance determined
                shift_list = path_to_change[new_start_index:] + path_to_change[:new_start_index]
                #  shifts the list by the distance determined
                layer.paths[j].points = shift_list + [shift_list[0]]


if __name__ == "__main__":
    pass
