from compas.geometry import Point
from compas_slicer.geometry import PrintPoint

__all__ = ['generate_z_hop']


## TODO: Maybe z_hop should be added always before print points with extruder toggle = False,
## regardless of their position in the paths

def generate_z_hop(printpoints_dict, z_hop=10):
    for key in printpoints_dict:

        # selects the first point in a path (pt0)
        printpoint_0 = printpoints_dict[key][0]
        pt0 = printpoint_0.pt

        # adds the vertical z_hop distance to the copied point
        pt0_copy = Point(pt0[0], pt0[1], pt0[2] + z_hop)

        z_hop_printpoint = PrintPoint(pt0_copy, printpoint_0.layer_height)
        z_hop_printpoint.parent_path = printpoint_0.parent_path
        z_hop_printpoint.extruder_toggle = False

        # insert z_hop point as first point
        printpoints_dict[key].insert(0, z_hop_printpoint)


if __name__ == "__main__":
    pass
