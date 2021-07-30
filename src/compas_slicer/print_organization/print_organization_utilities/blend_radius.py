from compas.geometry import norm_vector, Vector
import logging

logger = logging.getLogger('logger')

__all__ = ['set_blend_radius']


def set_blend_radius(print_organizer, d_fillet=10, buffer=0.3):
    """Sets the blend radius (filleting) for the robotic motion.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.slicers.BasePrintOrganizer`
    d_fillet: float
        Value to attempt to fillet with. Defaults to 10 mm.
    buffer: float
        Buffer to make sure that the blend radius is never too big.
        Defaults to 0.3.
    """

    logger.info("Setting blend radius")

    extruder_state = 0

    for printpoint, i, j, k in print_organizer.printpoints_indices_iterator():
        layer_key = 'layer_%d' % i
        path_key = 'path_%d' % j
        neighboring_items = print_organizer.get_printpoint_neighboring_items(layer_key, path_key, k)

        if not printpoint.wait_time:

            # if the extruder_toggle changes, it must be a new path and therefore the blend radius should be 0
            if extruder_state != printpoint.extruder_toggle:
                extruder_state = printpoint.extruder_toggle
                radius = 0.0

            else:

                radius = d_fillet
                if neighboring_items[0]:
                    radius = min(radius, norm_vector(Vector.from_start_end(neighboring_items[0].pt, printpoint.pt)) * buffer)

                if neighboring_items[1]:
                    radius = min(radius, norm_vector(Vector.from_start_end(neighboring_items[1].pt, printpoint.pt)) * buffer)

                radius = round(radius, 5)

        else:
            radius = 0.0  # 0.0 blend radius for points where the robot will pause and wait

        printpoint.blend_radius = radius


if __name__ == "__main__":
    pass
