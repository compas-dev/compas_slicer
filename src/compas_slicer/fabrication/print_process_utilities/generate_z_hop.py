from compas.geometry import Point
from compas_slicer.geometry import PrintPoint

__all__ = ['generate_z_hop']


## TODO: Maybe z_hop should be added always before print points with extruder toggle = False,
## regardless of their position in the paths

def generate_z_hop(printpoints, z_hop=10):
    printpoints_copy = []
    for i,printpoint in enumerate(printpoints):

        # selects the first point in a path (pt0)
        if printpoint.is_first_path_printpoint():
            # print('FIRST : ', i)
            # print('path_collection_index : ', printpoint.path_collection_index)
            # print('path_index : ', printpoint.path_index)
            # print('')
            pt0 = printpoint.pt

            z_hop_printpoint = PrintPoint(pt=Point(pt0[0], pt0[1], pt0[2] + z_hop),
                                          path_collection_index=printpoint.path_collection_index,
                                          path_index=printpoint.path_index,
                                          point_index=0,
                                          layer_height=printpoint.layer_height)
            z_hop_printpoint.parent_path = printpoint.parent_path
            z_hop_printpoint.extruder_toggle = False

            # insert on list the new printpoint
            printpoints_copy.append(z_hop_printpoint)

        printpoints_copy.append(printpoint)

    return printpoints_copy



if __name__ == "__main__":
    pass
