import logging

from compas.geometry import Point, distance_point_point

logger = logging.getLogger('logger')

__all__ = ['order_vertical_segments']


def order_vertical_segments(slicer, align_pt):
    """Orders the vertical segments in a specific way

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    align_pt: :class:`compas.geometry.Point`
        xx

    """
    logger.info("Changing order of vertical segments to start with the segment closest to the align_pt")

    new_order = []
    count = 1

    for i in range(len(slicer.layers)):

        if count < len(slicer.layers) - 1:
            # get current and previous point
            curr_pt0 = slicer.layers[count].paths[0].points[0]
            prev_pt0 = slicer.layers[count-1].paths[0].points[0]
            # calculate distance
            d_curr = distance_point_point(align_pt, curr_pt0)
            d_prev = distance_point_point(align_pt, prev_pt0)

            # check if the two layers start at the same height
            if curr_pt0[2] == prev_pt0[2]:

                # if they do, check which one is closest to the align_pt
                if d_curr >= d_prev:
                    new_order.append(slicer.layers[count-1])
                    new_order.append(slicer.layers[count])
                else:
                    new_order.append(slicer.layers[count])
                    new_order.append(slicer.layers[count-1])
                count += 2
            else:
                # otherwise, just append the prev layer
                new_order.append(slicer.layers[count-1])
                count += 1

    slicer.layers = new_order

if __name__ == "__main__":
    pass
