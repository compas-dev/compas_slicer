import compas_slicer
import logging

logger = logging.getLogger('logger')

__all__ = ['set_extruder_toggle',
           'override_extruder_toggle',
           'check_assigned_extruder_toggle']


def set_extruder_toggle(print_organizer, slicer):
    """Sets the extruder_toggle value for the printpoints.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    slicer: :class:`compas.slicers.BaseSlicer`
    """
    logger.info("Setting extruder toggle")

    pp_dict = print_organizer.printpoints_dict

    for i, layer in enumerate(slicer.layers):
        layer_key = 'layer_%d' % i
        is_vertical_layer = isinstance(layer, compas_slicer.geometry.VerticalLayer)
        is_brim_layer = layer.is_brim

        for j, path in enumerate(layer.paths):
            path_key = 'path_%d' % j
            is_closed_path = path.is_closed

            # --- decide if the path should be interrupted at the end
            interrupt_path = False

            if not is_closed_path:
                interrupt_path = True
                # open paths should always be interrupted

            if not is_vertical_layer and len(layer.paths) > 1:
                interrupt_path = True
                # horizontal layers with multiple paths should be interrupted so that the extruder
                # can travel from one path to the other, exception is added for the brim layers
                if is_brim_layer and (j + 1) % layer.number_of_brim_offsets != 0:
                    interrupt_path = False

            if is_vertical_layer and j == len(layer.paths) - 1:
                interrupt_path = True
                # the last path of a vertical layer should be interrupted

            # --- create extruder toggles
            path_printpoints = pp_dict[layer_key][path_key]
            for k, printpoint in enumerate(path_printpoints):

                if interrupt_path:
                    if k == len(path_printpoints) - 1:
                        printpoint.extruder_toggle = False
                    else:
                        printpoint.extruder_toggle = True
                else:
                    printpoint.extruder_toggle = True

        # set extruder toggle of last print point to false
        last_layer_key = 'layer_%d' % (len(pp_dict) - 1)
        last_path_key = 'path_%d' % (len(pp_dict[last_layer_key]) - 1)
        pp_dict[last_layer_key][last_path_key][-1].extruder_toggle = False


def override_extruder_toggle(print_organizer, override_value):
    """Overrides the extruder_toggle value for the printpoints with a user-defined value.

    Parameters
    ----------
    print_organizer: :class:`compas.print_organization.BasePrintOrganizer`
    override_value: bool
        Value to override the extruder_toggle values with.

    """
    pp_dict = print_organizer.printpoints_dict
    if isinstance(override_value, bool):
        for layer_key in pp_dict:
            for path_key in pp_dict[layer_key]:
                path_printpoints = pp_dict[layer_key][path_key]
                for printpoint in path_printpoints:
                    printpoint.extruder_toggle = override_value

    else:
        raise NameError("Override value must be of type bool")


def check_assigned_extruder_toggle(print_organizer):
    """ Checks that all the printpoints have an assigned extruder toggle. """
    pp_dict = print_organizer.printpoints_dict
    all_toggles_assigned = True
    for layer_key in pp_dict:
        for path_key in pp_dict[layer_key]:
            for pp in pp_dict[layer_key][path_key]:

                if pp.extruder_toggle is None:
                    all_toggles_assigned = False
    return all_toggles_assigned


if __name__ == "__main__":
    pass
