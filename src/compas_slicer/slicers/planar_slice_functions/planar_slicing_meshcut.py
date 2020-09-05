import numpy as np
from compas.geometry import Point, distance_point_point
from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer
from compas_slicer.geometry import PrintPoint
import meshcut

__all__ = ['create_planar_paths_meshcut']


def create_planar_paths_meshcut(mesh, layer_height):
    """Creates planar slices using the Meshcut library
    https://pypi.org/project/meshcut/ from Julien Rebetez

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        A compas mesh.
    layer_height : float
        A number representing the height between cutting planes.
    """
    # Convert compas mesh to meshcut mesh
    v = np.array(mesh.vertices_attributes('xyz'))
    vertices = v.reshape(-1, 3)  # vertices numpy array : #Vx3
    key_index = mesh.key_index()
    f = [[key_index[key] for key in mesh.face_vertices(fkey)] for fkey in mesh.faces()]
    faces = np.array(f)
    faces.reshape(-1, 3)  # faces numpy array : #Fx3
    vertices, faces = meshcut.merge_close_vertices(vertices, faces)
    meshcut_mesh = meshcut.TriangleMesh(vertices, faces)

    # get min and max z coordinates
    min_z, max_z = np.amin(vertices, axis=0)[2], np.amax(vertices, axis=0)[2]
    d = abs(min_z - max_z)
    no_of_layers = int(d / layer_height) + 1
    layers = []

    for i in range(no_of_layers):
        paths_per_layer = []
        # define plane
        # TODO check if adding 0.01 tolerance makes sense
        plane_origin = (0, 0, min_z + i * layer_height + 0.01)
        plane_normal = (0, 0, 1)
        plane = meshcut.Plane(plane_origin, plane_normal)
        # cut using meshcut cross_section_mesh
        meshcut_array = meshcut.cross_section_mesh(meshcut_mesh, plane)
        for j, item in enumerate(meshcut_array):
            # convert np array to list
            meshcut_list = item.tolist()
            # print(meshcut_list)
            points = [Point(p[0], p[1], p[2]) for p in meshcut_list]
            # append first point to form a closed polyline
            points.append(points[0])
            # TODO is_closed is always set to True, has to be checked
            is_closed = True

            # print_points = [PrintPoint(pt=p, layer_height=layer_height) for p in points]

            path = Path(points=points, is_closed=is_closed)
            paths_per_layer.append(path)

        layer = Layer(paths_per_layer)
        layers.append(layer)
    return layers


if __name__ == "__main__":
    pass
