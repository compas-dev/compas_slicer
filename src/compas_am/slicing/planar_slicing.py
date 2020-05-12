import numpy as np
import compas
from compas.datastructures import Mesh
from compas.geometry import  Point, distance_point_point
from compas_am.slicing.printpath import Contour
from compas_am.slicing.printpath import Layer

#####################################################
#### Meshcut planar slicing
#####################################################
import meshcut

def create_planar_contours_meshcut(mesh, layer_height):
    """Creates planar contours using the Meshcut library
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
    vertices = v.reshape(-1, 3) #vertices numpy array : #Vx3
    key_index = mesh.key_index()
    f = [[key_index[key] for key in mesh.face_vertices(fkey)] for fkey in mesh.faces()]
    faces = np.array(f)
    faces.reshape(-1, 3) #faces numpy array : #Fx3
    vertices, faces = meshcut.merge_close_vertices(vertices, faces)
    meshcut_mesh = meshcut.TriangleMesh(vertices, faces)

    # get min and max z coordinates
    min_z, max_z = np.amin(vertices, axis=0)[2], np.amax(vertices, axis=0)[2]
    d = abs(min_z - max_z)
    no_of_layers = int(d / layer_height)+1
    layers = []
    for i in range(no_of_layers):
        contours_per_layer = []
        # define plane
        # TODO check if addding 0.01 tolerance makes sense
        plane_origin = (0, 0,min_z + i*layer_height + 0.01)
        plane_normal = (0, 0, 1)
        plane = meshcut.Plane(plane_origin, plane_normal)
        # cut using meshcut cross_section_mesh
        meshcut_array = meshcut.cross_section_mesh(meshcut_mesh, plane)
        for j, item in enumerate(meshcut_array):
            # convert np array to list
            meshcut_list = item.tolist()
            #print(meshcut_list)
            points = [Point(p[0], p[1], p[2]) for p in meshcut_list]
            # append first point to form a closed polyline
            points.append(points[0])
            # TODO is_closed is always set to True, has to be checked
            is_closed = True
            c = Contour(points = points, is_closed = is_closed)
            contours_per_layer.append(c)
        l = Layer(contours_per_layer, None, None)
        layers.append(l)
    return layers


#####################################################
#### Compas numpy planar slicing
#####################################################
from compas.datastructures import mesh_contours_numpy

def create_planar_contours_numpy(mesh, layer_height):
    z = [mesh.vertex_attribute(key, 'z') for key in mesh.vertices()]
    z_bounds = max(z) - min(z)
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
                if len(points)>0:
                    threshold_closed = 15.0 #TODO: VERY BAD!! Threshold should not be hardcoded
                    is_closed = distance_point_point(points[0], points[-1]) < threshold_closed
                    c = Contour(points = points, is_closed = is_closed)
                    contours_per_layer.append(c)
            l = Layer(contours_per_layer, None, None)
            layers.append(l)
    return layers

if __name__ == "__main__":
    pass