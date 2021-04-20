import logging
from compas_slicer.utilities import find_next_printpoint
import math
from compas.geometry import Vector, normalize_vector

logger = logging.getLogger('logger')

__all__ = ['set_wait_time_on_sharp_corners',
           'set_wait_time_based_on_extruder_toggle',
           'override_wait_time']


def set_wait_time_on_sharp_corners(print_organizer, threshold=0.5 * math.pi, wait_time=0.3):
    """
    Sets a wait time at the sharp corners of the path, based on the angle threshold.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    threshold: float
        angle_threshold
    wait_time: float
        Time in seconds to introduce to add as a wait time
    """
    number_of_wait_points = 0
    for printpoint, i, j, k in print_organizer.printpoints_indices_iterator():
        neighbors = print_organizer.get_printpoint_neighboring_items('layer_%d' % i, 'path_%d' % j, k)
        prev_ppt = neighbors[0]
        next_ppt = neighbors[1]

        if prev_ppt and next_ppt:
            v_to_prev = normalize_vector(Vector.from_start_end(printpoint.pt, prev_ppt.pt))
            v_to_next = normalize_vector(Vector.from_start_end(printpoint.pt, next_ppt.pt))
            a = abs(Vector(*v_to_prev).angle(v_to_next))

            if a < threshold:
                printpoint.wait_time = wait_time
                printpoint.blend_radius = 0.0  # 0.0 blend radius for points where the robot will wait
                number_of_wait_points += 1
    logger.info('Added wait times for %d points' % number_of_wait_points)


def set_wait_time_based_on_extruder_toggle(print_organizer, wait_type, wait_time=0.3):
    """
    Sets a wait time for the printpoints, either before extrusion starts,
    after extrusion finishes, or in both cases.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    wait_type: str
        wait_before_extrusion:  sets a wait time before extrusion (extruder_toggle False to True)
        wait_after_extrusion: sets a wait time after extrusion (extruder_toggle True to False)
        wait_before_and_after_extrusion: sets a wait time before, and after extrusion
        wait_at_sharp_corners: sets a wait time at the sharp corners of the path
    wait_time: float
        Time in seconds to introduce to add as a wait time
    """

    for printpoint in print_organizer.printpoints_iterator():
        assert printpoint.extruder_toggle is not None, \
            'You need to set the extruder toggles first, before you can automatically set the wait time'

    logger.info("Setting wait time")

    for printpoint, i, j, k in print_organizer.printpoints_indices_iterator():
        number_of_wait_points = 0
        next_ppt = find_next_printpoint(print_organizer.printpoints_dict, i, j, k)

        # for the brim layer don't add any wait times
        if not print_organizer.slicer.layers[i].is_brim and next_ppt:
            if wait_type == "wait_before_extrusion":
                if printpoint.extruder_toggle is False and next_ppt.extruder_toggle is True:
                    next_ppt.wait_time = wait_time
                    next_ppt.blend_radius = 0.0
                    number_of_wait_points += 1
            elif wait_type == "wait_after_extrusion":
                if printpoint.extruder_toggle is True and next_ppt.extruder_toggle is False:
                    next_ppt.wait_time = wait_time
                    next_ppt.blend_radius = 0.0
                    number_of_wait_points += 1
            elif wait_type == "wait_before_and_after_extrusion":
                if printpoint.extruder_toggle is False and next_ppt.extruder_toggle is True:
                    next_ppt.wait_time = wait_time
                    next_ppt.blend_radius = 0.0
                    number_of_wait_points += 1
                if printpoint.extruder_toggle is True and next_ppt.extruder_toggle is False:
                    next_ppt.wait_time = wait_time
                    next_ppt.blend_radius = 0.0
                    number_of_wait_points += 1
            else:
                logger.error('Unknown wait type : ' + str(wait_type))

        logger.info('Added wait times for %d points' % number_of_wait_points)


def override_wait_time(print_organizer, override_value):
    """
    Overrides the wait_time value for the printpoints with a user-defined value.

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
