import pyclipper
from pyclipper import scale_from_clipper, scale_to_clipper
from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path
from compas.geometry import Point
import compas_slicer
import logging
from compas_slicer.post_processing import seams_align

logger = logging.getLogger('logger')

__all__ = ['generate_brim']


def generate_brim(slicer, layer_width, number_of_brim_offsets):
    """Creates a brim around the bottom contours of the print.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.PlanarSlicer`
        An instance of the compas_slicer.slicers.PlanarSlicer class
    layer_width: float
        A number representing the distance between brim contours
        (typically the width of a layer)
    number_of_brim_offsets: int
        Number of brim paths to add.
    """

    logger.info(
        "Generating brim with layer width: %.2f mm, consisting of %d layers" % (layer_width, number_of_brim_offsets))

    #  TODO: Add post_processing for merging several contours when the brims overlap.
    #  uses the default scaling factor of 2**32
    #  see: https://github.com/fonttools/pyclipper/wiki/Deprecating-SCALING_FACTOR
    SCALING_FACTOR = 2 ** 32

    if slicer.layers[0].is_raft:
        raise NameError("Raft found: cannot apply brim when raft is used, choose one")

    # (1) --- find if slicer has vertical or horizontal layers, and select which paths are to be offset.
    if isinstance(slicer.layers[0], compas_slicer.geometry.VerticalLayer):  # Vertical layers
        # then find all paths that lie on the print platform and make them brim.
        paths_to_offset, layers_i = slicer.find_vertical_layers_with_first_path_on_base()
        for i, first_path in zip(layers_i, paths_to_offset):
            slicer.layers[i].paths.remove(first_path)  # remove first path that will become part of the brim layer
        has_vertical_layers = True

    else:  # Horizontal layers
        # then replace the first layer with a brim layer.
        paths_to_offset = slicer.layers[0].paths
        has_vertical_layers = False

    assert len(paths_to_offset) > 0, 'Attention the brim generator did not find any path on the base. Please check the \
                                      paths of your slicer. '

    # (2) --- create new empty brim_layer
    brim_layer = Layer(paths=[])
    brim_layer.is_brim = True
    brim_layer.number_of_brim_offsets = number_of_brim_offsets

    # (3) --- create offsets and add them to the paths of the brim_layer
    for path in paths_to_offset:
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

        for i in range(number_of_brim_offsets):
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
            brim_layer.paths.append(new_path)

    brim_layer.paths.reverse()  # go from outside towards the object
    brim_layer.calculate_z_bounds()

    # (4) --- Add the brim layer to the slicer
    if not has_vertical_layers:
        slicer.layers[0] = brim_layer  # replace first layer
    else:
        slicer.layers.insert(0, brim_layer)  # insert brim layer as the first layer of the slicer

    seams_align(slicer, align_with="next_path")


if __name__ == "__main__":
    pass
