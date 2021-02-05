import logging
import itertools

from compas.geometry import Point, distance_point_point

logger = logging.getLogger('logger')

__all__ = ['reorder_vertical_layers']


def reorder_vertical_layers(slicer, align_with):
    """Re-orders the vertical layers in a specific way

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    align_with: str or :class:`compas.geometry.Point`
        x_axis       = reorders the vertical layers starting from the positive x-axis
        y_axis       = reorders the vertical layers starting from the positive y-axis
        Point(x,y,z) = reorders the vertical layers starting from a given Point
    """

    if align_with == "x_axis":
        align_pt = Point(2 ** 32, 0, 0)
    elif align_with == "y_axis":
        align_pt = Point(0, 2 ** 32, 0)
    elif isinstance(align_with, Point):
        align_pt = align_with
    else:
        raise NameError("Unknown align_with : " + str(align_with))

    logger.info("Re-ordering vertical layers to start with the vertical layer closest to: %s" % align_with)

    for layer in slicer.layers:
        assert layer.min_max_z_height[0] is not None and layer.min_max_z_height[1] is not None, \
            "To use the 'reorder_vertical_layers function you need first to calculate the layers' z_bounds. To do " \
            "that use the function 'Layer.calculate_z_bounds()'"

    # group vertical layers based on the min_max_z_height
    grouped_iter = itertools.groupby(slicer.layers, lambda x: x.min_max_z_height)
    grouped_layer_list = [list(group) for _key, group in grouped_iter]

    reordered_layers = []

    for grouped_layers in grouped_layer_list:
        distances = []
        for vert_layer in grouped_layers:
            # recreate head_centroid_pt as compas.Point
            head_centroid_pt = Point(vert_layer.head_centroid[0], vert_layer.head_centroid[1], vert_layer.head_centroid[2])
            # measure distance
            distances.append(distance_point_point(head_centroid_pt, align_pt))

        # sort lists based on closest distance to align pt
        grouped_new = [x for _, x in sorted(zip(distances, grouped_layers))]
        reordered_layers.append(grouped_new)

    # flatten list
    slicer.layers = [item for sublist in reordered_layers for item in sublist]


if __name__ == "__main__":
    pass
