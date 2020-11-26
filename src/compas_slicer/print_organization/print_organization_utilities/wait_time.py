import logging
logger = logging.getLogger('logger')

__all__ = ['set_wait_time',
           'override_wait_time']


def set_wait_time(print_organizer, wait_time):
    """Automatically sets a wait time for the printpoints.

    Sets a wait time for the printpoints if the extruder_toggle switches
    from False to True. Can be useful to add if there is a slight delay
    before the extruder starts to extrude.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    wait_time: float
        Time in seconds to introduce to add as a wait time
    """

    pp_dict = print_organizer.printpoints_dict

    for layer_key in pp_dict:
        for path_key in pp_dict[layer_key]:
            for pp in pp_dict[layer_key][path_key]:
                assert pp.extruder_toggle is not None, \
                    'You need to set the extruder toggles first, before you can automatically set the wait time'

    logger.info("Setting wait time")

    for i, layer_key in enumerate(pp_dict):
        for j, path_key in enumerate(pp_dict[layer_key]):
            for k, printpoint in enumerate(pp_dict[layer_key][path_key]):
                # compares the current point with the previous point
                # for the first point, compares it with the last point of the path
                curr = pp_dict[layer_key][path_key][k]
                prev = pp_dict[layer_key][path_key][k-1]

                if curr.extruder_toggle is True and prev.extruder_toggle is False:
                    if print_organizer.slicer.brim_toggle and layer_key == 'layer_0':
                        # for the brim layer don't add any wait times
                        pass
                    else:
                        # add wait time
                        printpoint.wait_time = wait_time


def override_wait_time(print_organizer, override_value):
    """Overrides the wait_time value for the printpoints with a user-defined value.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    override_value: float
        Value to override the wait_time values with.
    """

    pp_dict = print_organizer.printpoints_dict

    for layer_key in pp_dict:
        for path_key in pp_dict[layer_key]:
            path_printpoints = pp_dict[layer_key][path_key]
            for printpoint in path_printpoints:
                printpoint.wait_time = override_value


if __name__ == "__main__":
    pass