import numpy as np
from compas.geometry import Point
from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer
import logging
import meshcut
import progressbar

logger = logging.getLogger('logger')

__all__ = ['create_planar_paths_meshcut']


def create_planar_paths_meshcut(mesh, planes):
    """Creates planar slices using the Meshcut library
    https://pypi.org/project/meshcut/ from Julien Rebetez

    Considers all resulting paths as CLOSED paths.
    Attention, this is a very slow method.

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        A compas mesh.
    planes: list, compas.geometry.Plane
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

    layers = []
    with progressbar.ProgressBar(max_value=len(planes)) as bar:
        for i, plane in enumerate(planes):
            # z = plane.point[2]
            # logger.info('Cutting at height %.3f, %d percent done' % (
            #     z, int(100 * (z - min_z) / (max_z - min_z))))

            paths_per_layer = []

            plane = meshcut.Plane(plane.point, plane.normal)  # define plane

            meshcut_array = meshcut.cross_section_mesh(meshcut_mesh, plane)

            for _j, item in enumerate(meshcut_array):
                # convert np array to list
                meshcut_list = item.tolist()

                points = [Point(p[0], p[1], p[2]) for p in meshcut_list]
                is_closed = True  # TODO is_closed is always set to True, has to be checked
                path = Path(points=points, is_closed=is_closed)
                paths_per_layer.append(path)
            
            layer = Layer(paths_per_layer)
            layers.append(layer)

            # advance progressbar
            bar.update(i)
        
    return layers


if __name__ == "__main__":
    pass
