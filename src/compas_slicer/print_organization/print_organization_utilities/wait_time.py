import logging
from compas_slicer.utilities import find_next_printpoint

logger = logging.getLogger('logger')

__all__ = ['set_wait_time',
           'override_wait_time']


def set_wait_time(print_organizer, wait_type, wait_time):
    """Automatically sets a wait time for the printpoints.

    Sets a wait time for the printpoints, either before extrusion starts,
    after extrusion finishes, or in both cases.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    wait_type: str
        wait_before_extrusion:  sets a wait time before extrusion (extruder_toggle False to True)
        wait_after_extrusion: sets a wait time after extrusion (extruder_toggle True to False)
        wait_before_and_after_extrusion: sets a wait time before, and after extrusion
    wait_time: float
        Time in seconds to introduce to add as a wait time
    """

    pp_dict = print_organizer.printpoints_dict

    for printpoint in print_organizer.printpoints_iterator():
        assert printpoint.extruder_toggle is not None, \
            'You need to set the extruder toggles first, before you can automatically set the wait time'

    logger.info("Setting wait time")

    for printpoint, i, j, k in print_organizer.printpoints_indices_iterator():
        # compares the current point with the next point
        next_ppt = find_next_printpoint(pp_dict, i, j, k)

        # for the brim layer don't add any wait times
        if not print_organizer.slicer.layers[i].is_brim and next_ppt:
            if wait_type == "wait_before_extrusion":
                if printpoint.extruder_toggle is False and next_ppt.extruder_toggle is True:
                    next_ppt.wait_time = wait_time
            elif wait_type == "wait_after_extrusion":
                if printpoint.extruder_toggle is True and next_ppt.extruder_toggle is False:
                    next_ppt.wait_time = wait_time
            elif wait_type == "wait_before_and_after_extrusion":
                if printpoint.extruder_toggle is False and next_ppt.extruder_toggle is True:
                    next_ppt.wait_time = wait_time
                if printpoint.extruder_toggle is True and next_ppt.extruder_toggle is False:
                    next_ppt.wait_time = wait_time


def override_wait_time(print_organizer, override_value):
    """Overrides the wait_time value for the printpoints with a user-defined value.
    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    override_value: float
        Value to override the wait_time values with.
    """
    for printpoint in print_organizer.printpoints_iterator():
        printpoint.wait_time = override_value


if __name__ == "__main__":
    pass
