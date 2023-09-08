from compas.geometry import Vector
from compas_slicer.print_organization.print_organization_utilities.extruder_toggle import check_assigned_extruder_toggle
from compas_slicer.utilities import find_next_printpoint
import copy
import logging

logger = logging.getLogger('logger')

__all__ = ['add_safety_printpoints']


def add_safety_printpoints(print_organizer, z_hop=10.0):
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

    pp_dict = print_organizer.printpoints_dict
    pp_copy_dict = {}  # should not be altering the dict that we are iterating through > copy

    for i, layer_key in enumerate(pp_dict):
        pp_copy_dict[layer_key] = {}

        for j, path_key in enumerate(pp_dict[layer_key]):
            pp_copy_dict[layer_key][path_key] = []

            for k, printpoint in enumerate(pp_dict[layer_key][path_key]):
                #  add regular printing points
                pp_copy_dict[layer_key][path_key].append(printpoint)

                # add safety printpoints if there is an interruption
                if printpoint.extruder_toggle is False:

                    # safety ppt after current printpoint
                    pp_copy_dict[layer_key][path_key].append(create_safety_printpoint(printpoint, z_hop, False))

                    #  safety ppt before next printpoint (if there exists one)
                    next_ppt = find_next_printpoint(pp_dict, i, j, k)
                    if next_ppt:
                        if next_ppt.extruder_toggle is True:  # if it is a printing ppt
                            pp_copy_dict[layer_key][path_key].append(create_safety_printpoint(next_ppt, z_hop, False))

    #  finally, insert a safety print point at the beginning of the entire print
    try:
        safety_printpoint = create_safety_printpoint(pp_dict['layer_0']['path_0'][0], z_hop, False)
        pp_copy_dict['layer_0']['path_0'].insert(0, safety_printpoint)
    except KeyError as e:
        logger.exception(e)

    #  the safety printpoint has already been added at the end since the last printpoint extruder_toggle_type is False
    print_organizer.printpoints_dict = pp_copy_dict


def create_safety_printpoint(printpoint, z_hop, extruder_toggle):
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
    safety_printpoint.frame.point = safety_printpoint.pt
    safety_printpoint.extruder_toggle = extruder_toggle
    return safety_printpoint


if __name__ == "__main__":
    pass
