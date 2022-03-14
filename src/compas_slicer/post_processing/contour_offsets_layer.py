import pyclipper as pc

from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path

from compas.geometry import Point

__all__ = ['contour_offsets_layer']

def contour_offsets_layer(layer, layer_width, max_offsets):
    """
    Returns a layer with contour offset paths.

    Parameters
    ----------
    layer: :class:`compas_slicer.geometry.Layer`
        An instance of the compas_slicer.geometry.Layer class
    layer_wwidth: float
        A number specifying the contour offset distances that create the fermat spiral
    max_offsets: int
        A number specifying the maximum amount of contour offsets that serve as paths for the fermat spiral

    Returns
    -------
    The layer with the newly created offset paths.
    """

    SCALING_FACTOR = 2 ** 32

    paths_per_layer = []

    for path in layer.paths:
        #  evaluate per path
        xy_coords_for_clipper = []
        for point in path.points:
            # gets the X and Y coordinate since Clipper only does 2D offset operations
            xy_coords = [point[0], point[1]]
            xy_coords_for_clipper.append(xy_coords)

        #  initialise Clipper
        pco = pc.PyclipperOffset()
        pco.AddPath(pc.scale_to_clipper(xy_coords_for_clipper, SCALING_FACTOR), pc.JT_MITER,
                    pc.ET_CLOSEDPOLYGON)

        # set max offset iterations
        max_offset_number = max_offsets

        for i in range(max_offset_number + 1):
            #  iterate through a list of possible paths
            clipper_points_per_offset_path = []

            #  gets result
            result = pc.scale_from_clipper(pco.Execute(-1 * (i) * layer_width * SCALING_FACTOR), SCALING_FACTOR)

            # add new path if Clipper produces result
            if result:
                for xy in result[0]:
                    #  gets the X and Y coordinate from the Clipper result
                    x = xy[0]
                    y = xy[1]
                    z = path.points[0][2]

                    clipper_points_per_offset_path.append(Point(x, y, z))

                # adds the first point as the last point to form a closed contour
                clipper_points_per_offset_path = clipper_points_per_offset_path + [clipper_points_per_offset_path[0]]

                #  create a path for each contour
                new_path = Path(points=clipper_points_per_offset_path, is_closed=True)
                paths_per_layer.append(new_path)


    ## Whats happening here???
    #new_layer = Layer(paths=paths_per_layer)
    #new_layer.paths.reverse()  # go from outside towards the object
    return Layer(paths=paths_per_layer)

if __name__ == "__main__":
    pass