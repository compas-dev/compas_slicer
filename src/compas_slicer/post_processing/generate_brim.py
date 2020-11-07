import pyclipper
from pyclipper import scale_from_clipper, scale_to_clipper

from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path
from compas.geometry import Point

import logging
from compas_slicer.post_processing import seams_align

logger = logging.getLogger('logger')

__all__ = ['generate_brim']


def generate_brim(slicer, layer_width, number_of_brim_paths):
    """Creates a brim around the bottom contours of the print.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.PlanarSlicer`
        An instance of the compas_slicer.slicers.PlanarSlicer class
    layer_width: float
        A number representing the get_distance between brim contours
        (typically the width of a layer)
    number_of_brim_paths: int
        Number of brim paths to add.

    Returns
    -------
    None

    """
    logger.info(
        "Generating brim with layer width: %.2f mm, consisting of %d layers" % (layer_width, number_of_brim_paths))

    #  TODO: Add post_processing for merging several contours when the brims overlap.
    #  uses the default scaling factor of 2**32
    #  see: https://github.com/fonttools/pyclipper/wiki/Deprecating-SCALING_FACTOR
    SCALING_FACTOR = 2 ** 32

    paths_per_layer = []

    for path in slicer.layers[0].paths:
        #  evaluate per path
        xy_coords_for_clipper = []
        for point in path.points:
            # gets the X and Y coordinate since Clipper only does 2D offset operations
            xy_coords = [point[0], point[1]]
            xy_coords_for_clipper.append(xy_coords)

        #  initialise Clipper
        pco = pyclipper.PyclipperOffset()
        pco.AddPath(scale_to_clipper(xy_coords_for_clipper, SCALING_FACTOR), pyclipper.JT_MITER,
                    pyclipper.ET_CLOSEDPOLYGON)

        for i in range(number_of_brim_paths + 1):
            #  iterate through a list of brim paths
            clipper_points_per_brim_path = []

            #  gets result
            result = scale_from_clipper(pco.Execute((i) * layer_width * SCALING_FACTOR), SCALING_FACTOR)

            for xy in result[0]:
                #  gets the X and Y coordinate from the Clipper result
                x = xy[0]
                y = xy[1]
                z = path.points[0][2]

                clipper_points_per_brim_path.append(Point(x, y, z))

            # adds the first point as the last point to form a closed contour
            clipper_points_per_brim_path = clipper_points_per_brim_path + [clipper_points_per_brim_path[0]]

            #  create a path per brim contour
            new_path = Path(points=clipper_points_per_brim_path, is_closed=True)
            paths_per_layer.append(new_path)

    new_layer = Layer(paths=paths_per_layer)
    new_layer.paths.reverse()  # go from outside towards the object

    slicer.layers[0] = Layer(paths=paths_per_layer)

    seams_align(slicer, align_with="next_path")


if __name__ == "__main__":
    pass
