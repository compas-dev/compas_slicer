from compas_slicer.geometry import VerticalLayersManager
import logging

logger = logging.getLogger('logger')

__all__ = ['sort_into_vertical_layers']


def sort_into_vertical_layers(slicer, dist_threshold=25.0, max_paths_per_layer=None):
    """Sorts the paths from horizontal layers into Vertical Layers.

    Vertical Layers are layers at different heights that are grouped together by proximity
    of their center points. Can be useful for reducing travel time in a robotic printing
    process.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    dist_threshold: float
        The maximum get_distance that the centroids of two successive paths can have to belong in the same VerticalLayer
        Recommended value, slightly bigger than the layer height
    max_paths_per_layer: int
        Maximum number of layers that a vertical layer can consist of.
        If None, then the vertical layer has an unlimited number of layers.
    """
    logger.info("Sorting into Vertical Layers")

    vertical_layers_manager = VerticalLayersManager(dist_threshold, max_paths_per_layer)

    for layer in slicer.layers:
        for path in layer.paths:
            vertical_layers_manager.add(path)

    slicer.layers = vertical_layers_manager.layers
    logger.info("Number of vertical_layers: %d" % len(slicer.layers))


if __name__ == "__main__":
    pass
