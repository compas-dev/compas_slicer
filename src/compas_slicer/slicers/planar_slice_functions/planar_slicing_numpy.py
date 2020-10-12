import compas
from compas.datastructures import Mesh
from compas.geometry import Point, distance_point_point
from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer
import logging
logger = logging.getLogger('logger')

__all__ = ['create_planar_paths_numpy']


def create_planar_paths_numpy(mesh, min_z, max_z, planes):
    """
    Creates planar contours using the compas mesh_contours_numpy function. To be replaced with a better alternative

    Considers all resulting paths as CLOSED paths

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        A compas mesh.
    min_z: float
    max_z: float
    planes: list, compas.geometry.Plane
    """
    levels = [plane.point[2] for plane in planes]

    levels, np_layers = compas.datastructures.mesh_contours_numpy(mesh, levels=levels, density=20)


    layers = []

    for i, layer in enumerate(np_layers):
        z = levels[i]
        logger.info('Cutting at height %.3f, %d percent done' % (
            z, int(100 * (z - min_z) / (max_z - min_z))))

        print('')
        print('len(layer) : ', len(layer))
        for path in layer:
            print('len(path) : ', len(path))
            paths_per_layer = []
            for polygon2d in path:
                print('len(polygon2d) : ', len(polygon2d))

                print(polygon2d)
                points = [Point(p[0], p[1], levels[i]) for p in polygon2d[:-1]]


                if len(points) > 0:
                    # threshold_closed = 25.0  # TODO: Threshold should not be hardcoded
                    # is_closed = distance_point_point(points[0], points[-1]) < threshold_closed

                    # print_points = [PrintPoint(pt=p, layer_height=layer_height) for p in points]
                    path = Path(points=points, is_closed=True)

                    paths_per_layer.append(path)
            l = Layer(paths_per_layer)
            layers.append(l)
    return layers


if __name__ == "__main__":
    pass
