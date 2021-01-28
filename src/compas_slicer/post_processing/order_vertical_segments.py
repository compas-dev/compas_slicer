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

    for vert_layer in slicer.layers:
        print(vert_layer)

        for path in vert_layer.paths:
            print(path)
            print(path.points[0])

    for i in range(len(slicer.layers)):
        grouped_vert_layers = []

        # if slicer.layers.paths.points[0][2]

        grouped_vert_layers.append(slicer.layers[i])


if __name__ == "__main__":
    pass
