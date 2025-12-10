from __future__ import annotations

from loguru import logger
from typing import TYPE_CHECKING

import compas_slicer

if TYPE_CHECKING:
    from compas_slicer.print_organization import BasePrintOrganizer
    from compas_slicer.slicers import BaseSlicer


__all__ = ['set_extruder_toggle',
           'override_extruder_toggle',
           'check_assigned_extruder_toggle']


def set_extruder_toggle(print_organizer: BasePrintOrganizer, slicer: BaseSlicer) -> None:
    """Sets the extruder_toggle value for the printpoints.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    slicer: :class:`compas.slicers.BaseSlicer`
    """

    logger.info("Setting extruder toggle")

    for i, layer in enumerate(slicer.layers):
        is_vertical_layer = isinstance(layer, compas_slicer.geometry.VerticalLayer)
        is_brim_layer = layer.is_brim

        for j, path in enumerate(layer.paths):
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

            if i < len(slicer.layers)-1 and not slicer.layers[i+1].paths[0].is_closed:
                interrupt_path = True

            # --- create extruder toggles
            try:
                path_printpoints = print_organizer.printpoints[i][j]
            except (KeyError, IndexError):
                logger.exception(f"no path found for layer {i}")
            else:
                for k, printpoint in enumerate(path_printpoints):

                    if interrupt_path:
                        if k == len(path_printpoints) - 1:
                            printpoint.extruder_toggle = False
                        else:
                            printpoint.extruder_toggle = True
                    else:
                        printpoint.extruder_toggle = True

    # set extruder toggle of last print point to false
    try:
        print_organizer.printpoints[-1][-1][-1].extruder_toggle = False
    except (KeyError, IndexError) as e:
        logger.exception(e)


def override_extruder_toggle(print_organizer: BasePrintOrganizer, override_value: bool) -> None:
    """Overrides the extruder_toggle value for the printpoints with a user-defined value.

    Parameters
    ----------
    print_organizer: :class:`compas.print_organization.BasePrintOrganizer`
    override_value: bool
        Value to override the extruder_toggle values with.

    """
    assert isinstance(override_value, bool), "Override value must be of type bool"
    for printpoint in print_organizer.printpoints_iterator():
        printpoint.extruder_toggle = override_value


def check_assigned_extruder_toggle(print_organizer: BasePrintOrganizer) -> bool:
    """ Checks that all the printpoints have an assigned extruder toggle. """
    all_toggles_assigned = True
    for printpoint in print_organizer.printpoints_iterator():
        if printpoint.extruder_toggle is None:
            all_toggles_assigned = False
    return all_toggles_assigned


if __name__ == "__main__":
    pass
