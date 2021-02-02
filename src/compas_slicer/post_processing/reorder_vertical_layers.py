import logging
import itertools

from compas.geometry import Point, distance_point_point

logger = logging.getLogger('logger')

__all__ = ['reorder_vertical_layers']


def reorder_vertical_layers(slicer, align_pt):
    """Re-orders the vertical layers in a specific way

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    align_pt: :class:`compas.geometry.Point`
        xx
    """

    logger.info("Re-ordering vertical layers to start with the vertical layer closest to the align_pt")

    # group vertical layers based on the min_max_z_height
    grouped_iter = itertools.groupby(slicer.layers, lambda x: x.min_max_z_height)
    grouped_layer_list = [list(group) for _key, group in grouped_iter]

    reordered_layers = []

    for grouped_layers in grouped_layer_list:
        distances = []
        for vert_layer in grouped_layers:
            # recrate head_centroid_pt as compas.Point
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
