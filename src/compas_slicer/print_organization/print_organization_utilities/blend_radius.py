from compas.geometry import norm_vector, Vector

__all__ = ['set_blend_radius']


def set_blend_radius(print_organizer, dfillet=10, buffer=0.3):
    """Sets the blend radius (filleting) to use.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.slicers.PrintOrganizer`
    d_fillet: float
        Value to attempt to fillet with. Defaults to 10 mm.
    buffer:
        Buffer to make sure that the blend radius is never to big.
        Defaults to 0.3.

    """

    pp_dict = print_organizer.printpoints_dict

    for layer_key in pp_dict:
        for path_key in pp_dict[layer_key]:
            path_printpoints = pp_dict[layer_key][path_key]
            for i, printpoint in enumerate(path_printpoints):
                neighboring_items = print_organizer.get_printpoint_neighboring_items(layer_key, path_key, i)

                radius = dfillet
                if neighboring_items[0]:
                    radius = min(radius,
                                 norm_vector(Vector.from_start_end(neighboring_items[0].pt, printpoint.pt)) * buffer)

                if neighboring_items[1]:
                    radius = min(radius,
                                 norm_vector(Vector.from_start_end(neighboring_items[1].pt, printpoint.pt)) * buffer)

                radius = round(radius, 5)

                printpoint.blend_radius = radius


if __name__ == "__main__":
    pass
