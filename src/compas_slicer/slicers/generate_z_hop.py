import copy

from compas.geometry import Point

__all__ = ['generate_z_hop']

def generate_z_hop(print_paths, z_hop=10):
    for layer in print_paths:
        for contour in layer.contours:
            # selects the first point in a contour (pt0)
            pt0 = contour.points[0]
            # creates a (deep) copy
            pt0_copy = copy.deepcopy(pt0)
            # adds the vertical z_hop distance to the copied point
            pt0_copy = Point(pt0[0], pt0[1], pt0[2] + z_hop)
            # insert z_hop point as first point
            contour.points.insert(0, pt0_copy) 
            # and append as last point
            contour.points.append(pt0_copy) 
            
if __name__ == "__main__":
    pass