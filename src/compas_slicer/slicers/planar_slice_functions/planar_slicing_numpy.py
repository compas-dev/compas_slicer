import compas
from compas.datastructures import Mesh
from compas.geometry import Point, distance_point_point
from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer

__all__ = ['create_planar_paths_numpy']

##TODO: Improve this function

def create_planar_paths_numpy(mesh, layer_height):
    """
    Creates planar contours using the compas mesh_contours_numpy function. To be replaced with a better alternative

    Considers all resulting paths as CLOSED paths

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        The mesh to be sliced 
    layer_height : float
        A number representing the height between cutting planes.
    """
    z = [mesh.vertex_attribute(key, 'z') for key in mesh.vertices()]
    levels = []
    p = min(z)
    while p < max(z):
        levels.append(p)
        p += layer_height
    levels, compound_contours = compas.datastructures.mesh_contours_numpy(mesh, levels=levels, density=10)

    layers = []

    for i, compound_contour in enumerate(compound_contours):
        for path in compound_contour:
            contours_per_layer = []
            for polygon2d in path:
                points = [Point(p[0], p[1], levels[i]) for p in polygon2d[:-1]]
                if len(points) > 0:
                    threshold_closed = 25.0  # TODO: VERY BAD!! Threshold should not be hardcoded
                    is_closed = distance_point_point(points[0], points[-1]) < threshold_closed

                    # print_points = [PrintPoint(pt=p, layer_height=layer_height) for p in points]
                    path = Path(points=points, is_closed=is_closed)

                    contours_per_layer.append(path)
            l = Layer(contours_per_layer)
            layers.append(l)
    return layers


if __name__ == "__main__":
    pass
