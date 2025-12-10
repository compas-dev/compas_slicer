from __future__ import annotations

import copy
from loguru import logger
from typing import TYPE_CHECKING

from compas.geometry import Vector

from compas_slicer.geometry import PrintLayer, PrintPath, PrintPoint
from compas_slicer.print_organization.print_organization_utilities.extruder_toggle import check_assigned_extruder_toggle
from compas_slicer.utilities import find_next_printpoint

if TYPE_CHECKING:
    from compas_slicer.print_organization import BasePrintOrganizer


__all__ = ['add_safety_printpoints']


def add_safety_printpoints(print_organizer: BasePrintOrganizer, z_hop: float = 10.0) -> None:
    """Generates a safety print point at the interruptions of the print paths.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
        An instance of the BasePrintOrganizer class.
    z_hop: float
        Vertical distance (in millimeters) of the safety point above the PrintPoint.
    """
    assert check_assigned_extruder_toggle(print_organizer), \
        'You need to set the extruder toggles first, before you can create safety points'
    logger.info("Generating safety print points with height " + str(z_hop) + " mm")

    from compas_slicer.geometry import PrintPointsCollection

    new_collection = PrintPointsCollection()

    for i, layer in enumerate(print_organizer.printpoints):
        new_layer = PrintLayer()

        for j, path in enumerate(layer):
            new_path = PrintPath()

            for k, printpoint in enumerate(path):
                #  add regular printing points
                new_path.printpoints.append(printpoint)

                # add safety printpoints if there is an interruption
                if printpoint.extruder_toggle is False:

                    # safety ppt after current printpoint
                    new_path.printpoints.append(create_safety_printpoint(printpoint, z_hop, False))

                    #  safety ppt before next printpoint (if there exists one)
                    next_ppt = find_next_printpoint(print_organizer.printpoints, i, j, k)
                    if next_ppt and next_ppt.extruder_toggle is True:  # if it is a printing ppt
                        new_path.printpoints.append(create_safety_printpoint(next_ppt, z_hop, False))

            new_layer.paths.append(new_path)

        new_collection.layers.append(new_layer)

    #  finally, insert a safety print point at the beginning of the entire print
    try:
        safety_printpoint = create_safety_printpoint(new_collection[0][0][0], z_hop, False)
        new_collection[0][0].printpoints.insert(0, safety_printpoint)
    except (KeyError, IndexError) as e:
        logger.exception(e)

    #  the safety printpoint has already been added at the end since the last printpoint extruder_toggle_type is False
    print_organizer.printpoints = new_collection


def create_safety_printpoint(printpoint: PrintPoint, z_hop: float, extruder_toggle: bool) -> PrintPoint:
    """

    Parameters
    ----------
    printpoint: :class: 'compas_slicer.geometry.PrintPoint'
    z_hop: float
    extruder_toggle: bool

    Returns
    ----------
    :class: 'compas_slicer.geometry.PrintPoint'
    """

    pt0 = printpoint.pt
    safety_printpoint = copy.deepcopy(printpoint)
    safety_printpoint.pt = pt0 + Vector(0, 0, z_hop)
    if safety_printpoint.frame is not None:
        safety_printpoint.frame.point = safety_printpoint.pt
    safety_printpoint.extruder_toggle = extruder_toggle
    return safety_printpoint


if __name__ == "__main__":
    pass
