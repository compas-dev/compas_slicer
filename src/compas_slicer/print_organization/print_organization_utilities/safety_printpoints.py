from compas.geometry import Vector
import copy
import logging

logger = logging.getLogger('logger')

__all__ = ['add_safety_printpoints']


def add_safety_printpoints(print_organizer, z_hop=20.0):
    """Generates a safety print point at the interruptions of the print paths.

    Parameters
    ----------
    print_organizer: :class:`compas.print_organization.PrintOrganizer`
        An instance of the PrintOrganizer class.
    z_hop: float
        Vertical distance (in millimeters) of the safety point above the PrintPoint.
    """
    for layer_key in print_organizer.printpoints_dict:
        for path_key in print_organizer.printpoints_dict[layer_key]:
            for pp in print_organizer.printpoints_dict[layer_key][path_key]:
                assert pp.extruder_toggle is not None, \
                    'You need to set the extruder toggles first, before you can create safety points'

    logger.info("Generating safety print points with height " + str(z_hop) + " mm")

    pp_dict = print_organizer.printpoints_dict
    pp_copy_dict = {}  # should not be altering the dict that we are iterating through > copy

    # get last layer key and path
    last_layer_key = 'layer_%d' % (len(pp_dict) - 1)
    last_path_key = 'path_%d' % (len(pp_dict[last_layer_key]) - 1)
    # check if there are multiple paths in the last layer
    multiple_paths_in_last_layer = False if len(pp_dict[last_layer_key]) == 1 else True

    for layer_key in pp_dict:
        pp_copy_dict[layer_key] = {}

        for path_key in pp_dict[layer_key]:
            pp_copy_dict[layer_key][path_key] = []

            for i, printpoint in enumerate(pp_dict[layer_key][path_key]):
                # add a safety point before the first point of a path

                # if not the first point of the entire print
                if printpoint is not pp_dict['layer_0']['path_0'][0]:
                    # or the first point of last layer (except when there are multiple paths in last layer)
                    if printpoint is not pp_dict[last_layer_key][last_path_key][0] or multiple_paths_in_last_layer:
                        # check if the last point of a path is set to False
                        if i == 0 and not pp_dict[layer_key][path_key][-1].extruder_toggle:
                            # if False, add safety point
                            safety_printpoint = create_safety_printpoint(printpoint, z_hop, False)
                            pp_copy_dict[layer_key][path_key].append(safety_printpoint)

                #  regular printing points
                pp_copy_dict[layer_key][path_key].append(printpoint)

                #  adds a safety point after every printpoint that has extruder_toggle = False
                if printpoint.extruder_toggle is False:
                    safety_printpoint = create_safety_printpoint(printpoint, z_hop, False)
                    pp_copy_dict[layer_key][path_key].append(safety_printpoint)

    #  insert a safety print point at the beginning
    safety_printpoint = create_safety_printpoint(pp_dict['layer_0']['path_0'][0], z_hop, False)
    pp_copy_dict['layer_0']['path_0'].insert(0, safety_printpoint)

    #  the safety printpoint has already been added at the end since the last printpoint extruder_toggle_type is False
    print_organizer.printpoints_dict = pp_copy_dict


def create_safety_printpoint(printpoint, z_hop, extruder_toggle):
    pt0 = printpoint.pt
    safety_printpoint = copy.deepcopy(printpoint)
    safety_printpoint.pt = pt0 + Vector(0, 0, z_hop)
    safety_printpoint.extruder_toggle = extruder_toggle
    return safety_printpoint


if __name__ == "__main__":
    pass
