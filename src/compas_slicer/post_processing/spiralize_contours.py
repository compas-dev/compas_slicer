import logging
from compas.geometry import Point

logger = logging.getLogger('logger')

__all__ = ['spiralize_contours']


def spiralize_contours(slicer):
    """Spiralizes contours. Only supports a constant layer height.
    Can only be used for geometries consisting out of a single contour (vases).

    Parameters
    ----------
    slicer: :class: 'compas_slicer.slicers.PlanarSlicer'
        An instance of the compas_slicer.slicers.PlanarSlicer class.
    """
    # retrieves layer height by subtracting z of first point of layer 1 from layer 0
    layer_height = slicer.layers[1].paths[0].points[0][2] - slicer.layers[0].paths[0].points[0][2]

    for i, layer in enumerate(slicer.layers):
        if len(layer.paths) == 1:
            for path in layer.paths:
                for i, point in enumerate(path.points):
                    # get the number of points in a layer
                    no_of_points = len(path.points)
                    # calculates distance to move
                    distance_to_move = layer_height / no_of_points
                    # adds the distance to move to the z value and create new points
                    path.points[i] = Point(point[0], point[1], point[2] + (i*distance_to_move))
                # removes the first item to create a smooth transition to the next layer
                path.points.pop(0)
        else:
            logger.warning("Spiralize contours only works for layers consisting out of a single path, contours were not changed, spiralize contour skipped for layer %i" % i)


if __name__ == "__main__":
    pass
