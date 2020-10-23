from compas.geometry import Vector
import copy

__all__ = ['add_safety_printpoints']


def add_safety_printpoints(printpoints_dict, z_hop=20):
    """Generates a safety print point at the interruptions of the print paths.

    Parameters
    ----------
    printpoints_dict : dictionary
        The PrintPoints as a dictionary.
    z_hop : float
        The value (in mm) to use for the height of the safety command.
    """
    print_points_copy_dict = {}  # should not be altering the dict that we are iterating through > copy
    for layer_key in printpoints_dict:
        print_points_copy_dict[layer_key] = {}

        for path_key in printpoints_dict[layer_key]:
            print_points_copy_dict[layer_key][path_key] = []

            # get length of path to determine last point
            path_len = len(printpoints_dict[layer_key][path_key])

            for i, printpoint in enumerate(printpoints_dict[layer_key][path_key]):
                # add a safety point before the first point
                # if not the first point of the entire print
                if printpoint is not printpoints_dict['layer_0']['path_0'][0]:
                    if i == 0 and not printpoints_dict[layer_key][path_key][path_len-1].extruder_toggle:
                        safety_printpoint = safety_printpoint = create_safety_printpoint(printpoint, z_hop, False)
                        print_points_copy_dict[layer_key][path_key].append(safety_printpoint)

                #  regular printing points
                print_points_copy_dict[layer_key][path_key].append(printpoint)

                #  adds a safety point after every printpoint that has extruder_toggle = False
                if printpoint.extruder_toggle is False:
                    safety_printpoint = create_safety_printpoint(printpoint, z_hop, False)
                    print_points_copy_dict[layer_key][path_key].append(safety_printpoint)

    #  insert a safety print point at the beginning
    safety_printpoint = create_safety_printpoint(printpoints_dict['layer_0']['path_0'][0], z_hop, False)
    print_points_copy_dict['layer_0']['path_0'].insert(0, safety_printpoint)

    #  the safety printpoint has already been added at the end since the last printpoint extruder_toggle_type is False
    return print_points_copy_dict


def create_safety_printpoint(printpoint, z_hop, extruder_toggle):
    pt0 = printpoint.pt
    safety_printpoint = copy.deepcopy(printpoint)
    safety_printpoint.pt = pt0 + Vector(0, 0, z_hop)
    safety_printpoint.extruder_toggle = extruder_toggle
    return safety_printpoint


if __name__ == "__main__":
    pass
