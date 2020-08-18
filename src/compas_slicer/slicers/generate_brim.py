import pyclipper

from pyclipper import scale_from_clipper, scale_to_clipper

from compas_slicer.geometry import Layer
from compas_slicer.geometry import Contour
from compas_slicer.geometry import AdvancedPrintPoint

from compas.geometry import Point

__all__ = ['generate_brim']


def generate_brim(print_paths, layer_width, number_of_brim_layers):
    """Creates a brim around the bottom contours of the print.

    Parameters
    ----------
    print_paths : list
        A list of compas_slicer.geometry.Layer instances
    layer_width : float
        A number representing the distance between brim contours 
        (typically the width of a layer)
    number_of_brim_layers : int
        Number of brim layers to add.
    """
    # TODO: Add functionality for merging several contours when the brims overlap.  

    # uses the default scaling factor of 2**32
    # see: https://github.com/fonttools/pyclipper/wiki/Deprecating-SCALING_FACTOR
    SCALING_FACTOR = 2**32

    # gets the same layer height as used by the first point of the first layer
    layer_height = print_paths[0].contours[0].printpoints[0].layer_height

    contours_per_layer = []

    for contour in print_paths[0].contours:  
        xy_coords_for_clipper = []
        for printpoint in contour.printpoints:
            # gets the X and Y coordinate since Clipper only does 2D offset operations
            xy_coords = [printpoint.pt[0], printpoint.pt[1]]
            xy_coords_for_clipper.append(xy_coords)

        # initialise Clipper
        pco = pyclipper.PyclipperOffset()
        pco.AddPath(scale_to_clipper(xy_coords_for_clipper, SCALING_FACTOR), pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)
        
        clipper_contours = []

        for i in range(number_of_brim_layers):
            clipper_points_per_contour = []

            # gets result
            result = scale_from_clipper(pco.Execute((i+1)*layer_width*SCALING_FACTOR), SCALING_FACTOR)

            for xy in result[0]:
                # gets the X and Y coordinate from the Clipper result
                x = xy[0]
                y = xy[1]
                # get the Z coordinate from the previous slicing result
                z = contour.printpoints[0].pt[2]

                clipper_pt = Point(x,y,z)
                
                # creates new points
                p = AdvancedPrintPoint(pt=clipper_pt,
                                            layer_height=layer_height,
                                            up_vector=None,
                                            mesh=None,
                                            extruder_toggle=None)

                clipper_points_per_contour.append(p)
        
            # adds first point again to form a closed polygon since clipper removes this point
            clipper_points_per_contour = clipper_points_per_contour + [clipper_points_per_contour[0]]
            # create new contours for the Clipper offsets
            c_clipper = Contour(points=clipper_points_per_contour, is_closed=True)
            clipper_contours.append(c_clipper)

        # all contours for the layer
        contours_per_layer = contours_per_layer + [contour] + clipper_contours

    # replace first layer of print paths with the new layer that includes the Brim
    print_paths[0] = Layer(contours_per_layer, None, None)

    return print_paths

if __name__ == "__main__":
    pass
