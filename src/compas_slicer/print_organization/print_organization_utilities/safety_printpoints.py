from compas.geometry import Vector
from compas_slicer.print_organization.print_organization_utilities.extruder_toggle import check_assigned_extruder_toggle
import copy
import logging

logger = logging.getLogger('logger')

__all__ = ['add_safety_printpoints']


def add_safety_printpoints_a(print_organizer, z_hop=10.0):
    """Generates a safety print point at the interruptions of the print paths.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
        An instance of the BasePrintOrganizer class.
    z_hop: float
        Vertical distance (in millimeters) of the safety point above the PrintPoint.
    """
    check_assigned_extruder_toggle(print_organizer)
    logger.info("Generating safety print points with height " + str(z_hop) + " mm")

    pp_dict = print_organizer.printpoints_dict
    pp_copy_dict = {}  # should not be altering the dict that we are iterating through > copy

    print('print_organizer.slicer.number_of_brim_paths : ', print_organizer.slicer.number_of_brim_paths)

    for i, layer_key in enumerate(pp_dict):
        pp_copy_dict[layer_key] = {}

        for j, path_key in enumerate(pp_dict[layer_key]):
            pp_copy_dict[layer_key][path_key] = []

            for k, printpoint in enumerate(pp_dict[layer_key][path_key]):
                #  regular printing points
                pp_copy_dict[layer_key][path_key].append(printpoint)

                # add safety printpoints if there is an interruption
                if printpoint.extruder_toggle is False:

                    # safety ppt after current printpoint
                    pp_copy_dict[layer_key][path_key].append(create_safety_printpoint(printpoint, z_hop, False))

                    #  safety ppt before next printpoint (if there exists one)
                    next_ppt = find_next_printpoint(pp_dict, layer_key, path_key, i, j, k)
                    if next_ppt:
                        if next_ppt.extruder_toggle is True:  # if it is a printing ppt
                            pp_copy_dict[layer_key][path_key].append(create_safety_printpoint(next_ppt, z_hop, False))

    #  finally, insert a safety print point at the beginning of the entire print
    safety_printpoint = create_safety_printpoint(pp_dict['layer_0']['path_0'][0], z_hop, False)
    pp_copy_dict['layer_0']['path_0'].insert(0, safety_printpoint)

    #  the safety printpoint has already been added at the end since the last printpoint extruder_toggle_type is False
    print_organizer.printpoints_dict = pp_copy_dict


def find_next_printpoint(pp_dict, layer_key, path_key, i, j, k):
    """ Find the next printpoint of the current printpoint. """
    next_ppt = None
    if k < len(pp_dict[layer_key][path_key]) - 1:  # If there are more ppts in the current path, then take the next ppt
        next_ppt = pp_dict[layer_key][path_key][k + 1]
    else:
        if j < len(pp_dict[layer_key]) - 1:  # Otherwise take the next path if there are more paths in the current layer
            next_ppt = pp_dict[layer_key]['path_%d' % (j + 1)][0]
        else:
            if i < len(pp_dict) - 1:  # Otherwise take the next layer if there are more layers in the current slicer
                next_ppt = pp_dict['layer_%d' % (i + 1)]['path_0'][0]
    return next_ppt


# def add_safety_printpoints_OLD(print_organizer, z_hop=10.0):
#     check_assigned_extruder_toggle(print_organizer)
#
#     logger.info("Generating safety print points with height " + str(z_hop) + " mm")
#
#     pp_dict = print_organizer.printpoints_dict
#     pp_copy_dict = {}  # should not be altering the dict that we are iterating through > copy
#
#     # get last layer key
#     last_layer_key = 'layer_%d' % (len(pp_dict) - 1)
#     # check if there are multiple paths in the last layer
#     multiple_paths_in_last_layer = False if len(pp_dict[last_layer_key]) == 1 else True
#
#     for i, layer_key in enumerate(pp_dict):
#         pp_copy_dict[layer_key] = {}
#
#         for j, path_key in enumerate(pp_dict[layer_key]):
#             pp_copy_dict[layer_key][path_key] = []
#
#             for k, printpoint in enumerate(pp_dict[layer_key][path_key]):
#                 #  regular printing points
#                 pp_copy_dict[layer_key][path_key].append(printpoint)
#
#                 # adds a safety point after every printpoint that has extruder_toggle = False
#                 # and before the first point of the path
#                 if printpoint.extruder_toggle is False:
#                     # create safety printpoint
#                     safety_printpoint = create_safety_printpoint(printpoint, z_hop, False)
#                     # if there is a brim in the first layer, don't add the safety points to the brim
#                     if print_organizer.slicer.brim_toggle and layer_key == 'layer_0':
#                         brim_start_path = 'path_%d' % (j - print_organizer.slicer.number_of_brim_paths)
#                         start_safety_printpoint = create_safety_printpoint(pp_dict[layer_key][brim_start_path][0],
#                                                                            z_hop,
#                                                                            False)
#                         # for the first point of the print (layer_0, path_0), don't add a safety point in the beginning
#                         if brim_start_path != 'path_0':
#                             pp_copy_dict[layer_key][brim_start_path].insert(0,
#                                                                             start_safety_printpoint)  # insert at the beginning
#                         # if the next layer after the brim (layer 1) has only one path, don't add a safety point at the end
#                         if len(pp_dict['layer_1']) != 1:
#                             pp_copy_dict[layer_key][path_key].append(safety_printpoint)  # append at the end
#
#                     # for layers without a brim, append safety point at the beginning and end
#                     else:
#                         # except if the first point of the print since it is added later
#                         if layer_key == 'layer_0' and path_key == 'path_0':
#                             pp_copy_dict[layer_key][path_key].append(safety_printpoint)  # append only at the end
#                         # and except for last layer if it does not have multiple paths
#                         elif layer_key == last_layer_key and not multiple_paths_in_last_layer:
#                             pp_copy_dict[layer_key][path_key].append(safety_printpoint)  # append only at the end
#                         else:
#                             pp_copy_dict[layer_key][path_key].insert(0, safety_printpoint)
#                             pp_copy_dict[layer_key][path_key].append(safety_printpoint)  # append at the end
#
#     #  insert a safety print point at the beginning
#     safety_printpoint = create_safety_printpoint(pp_dict['layer_0']['path_0'][0], z_hop, False)
#     pp_copy_dict['layer_0']['path_0'].insert(0, safety_printpoint)
#
#     #  the safety printpoint has already been added at the end since the last printpoint extruder_toggle_type is False
#     print_organizer.printpoints_dict = pp_copy_dict


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
    safety_printpoint.extruder_toggle = extruder_toggle
    return safety_printpoint


if __name__ == "__main__":
    pass
