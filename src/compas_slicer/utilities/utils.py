import os
import json
import logging
import statistics
from compas.geometry import Point, distance_point_point_sqrd, normalize_vector
from compas.geometry import Vector, closest_point_in_cloud, length_vector
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

logger = logging.getLogger('logger')

__all__ = ['get_output_directory',
           'save_to_json',
           'load_from_json',
           'total_length_of_dictionary',
           'flattened_list_of_dictionary',
           'interrupt',
           'point_list_to_dict',
           'get_closest_mesh_vkey',
           'get_closest_mesh_normal_to_pt',
           'get_closest_pt_index',
           'get_closest_pt',
           'plot_networkx_graph',
           'get_mesh_vertex_coords_with_attribute',
           'get_dict_key_from_value',
           'get_closest_mesh_normal_to_pt',
           'smooth_vectors',
           'get_normal_of_path_on_xy_plane',
           'get_all_files_with_name']


def get_output_directory(path):
    """
    Checks if a directory with the name 'output' exists in the path. If not it creates it.

    Attributes
    ----------
    path : string
        The path where the 'output' directory will be created

    Returns
    ----------
    path : string
        The path to the new (or already existing) 'output' directory
    """
    output_dir = os.path.join(path, 'output')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    return output_dir


def get_closest_pt_index(pt, pts):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    ci = closest_point_in_cloud(point=pt, cloud=pts)[2]
    # distances = [distance_point_point_sqrd(p, pt) for p in pts]
    # ci = distances.index(min(distances))
    return ci


def get_closest_pt(pt, pts):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    ci = closest_point_in_cloud(point=pt, cloud=pts)[2]
    return pts[ci]


def smooth_vectors(vectors, strength, iterations):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    for _ in range(iterations):
        for i, n in enumerate(vectors):
            if 0 < i < len(vectors) - 1:
                neighbors_average = (vectors[i - 1] + vectors[i + 1]) * 0.5
            else:
                neighbors_average = n
            vectors[i] = n * (1 - strength) + neighbors_average * strength
    return vectors


#######################################
#  json

def save_to_json(data, filepath, name):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    filename = os.path.join(filepath, name)
    logger.info("Saving to json: " + filename)
    with open(filename, 'w') as f:
        f.write(json.dumps(data, indent=3, sort_keys=True))


def load_from_json(filepath, name):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    filename = os.path.join(filepath, name)
    with open(filename, 'r') as f:
        data = json.load(f)
    logger.info("Loaded json: " + filename)
    return data


#######################################
#  mesh utils

def check_triangular_mesh(mesh):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    for f_key in mesh.faces():
        vs = mesh.face_vertices(f_key)
        if len(vs) != 3:
            raise TypeError("Found a quad at face key: " + str(f_key) + " ,number of face vertices:" + str(
                len(vs)) + ". \nOnly triangular meshes supported.")


def get_closest_mesh_vkey(mesh, pt):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """
    # cloud = [Point(data['x'], data['y'], data['z']) for v_key, data in mesh.vertices(data=True)]
    # closest_index = compas.geometry.closest_point_in_cloud(pt, cloud)[2]
    vertex_tupples = [(v_key, Point(data['x'], data['y'], data['z'])) for v_key, data in mesh.vertices(data=True)]
    vertex_tupples = sorted(vertex_tupples, key=lambda v_tupple: distance_point_point_sqrd(pt, v_tupple[1]))
    closest_vkey = vertex_tupples[0][0]

    return closest_vkey


def get_closest_mesh_normal_to_pt(mesh, pt):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    closest_vkey = get_closest_mesh_vkey(mesh, pt)
    v = mesh.vertex_normal(closest_vkey)
    return Vector(v[0], v[1], v[2])


def get_mesh_vertex_coords_with_attribute(mesh, attr, value):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    pts = []
    for vkey, data in mesh.vertices(data=True):
        if data[attr] == value:
            pts.append(mesh.vertex_coordinates(vkey))
    return pts


def get_normal_of_path_on_xy_plane(k, point, path, mesh):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    # find mesh normal is not really needed in the 2D case of planar slicer
    # instead we only need the normal of the curve based on the neighboring pts
    if (0 < k < len(path.points) - 1) or path.is_closed:
        prev_pt = path.points[k - 1]
        next_pt = path.points[(k + 1) % len(path.points)]
        v1 = np.array(normalize_vector(Vector.from_start_end(prev_pt, point)))
        v2 = np.array(normalize_vector(Vector.from_start_end(point, next_pt)))
        v = (v1 + v2) * 0.5
        normal = [-v[1], v[0], v[2]]  # rotate 90 degrees COUNTER-clockwise on the xy plane

    else:
        if k == 0:
            next_pt = path.points[k + 1]
            v = normalize_vector(Vector.from_start_end(point, next_pt))
            normal = [-v[1], v[0], v[2]]  # rotate 90 degrees COUNTER-clockwise on the xy plane
        else:  # k == len(path.points)-1:
            prev_pt = path.points[k - 1]
            v = normalize_vector(Vector.from_start_end(point, prev_pt))
            normal = [v[1], -v[0], v[2]]  # rotate 90 degrees clockwise on the xy plane

    # TODO: Attention! This is just a workaround! find the source of the problem and imrpove this!
    if length_vector(normal) == 0:
        # logger.error('Attention! It looks like you might have some duplicated points')
        normal = get_closest_mesh_normal_to_pt(point, mesh)

    normal = normalize_vector(normal)
    normal = Vector(*list(normal))
    return normal


#######################################
#  networkx graph

def plot_networkx_graph(G):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    plt.subplot(121)
    nx.draw(G, with_labels=True, font_weight='bold', node_color=range(len(list(G.nodes()))))
    plt.show()


#######################################
#  dict utils

def point_list_to_dict(pts_list):
    """
    Turns a list of compas.geometry.Point into a dictionary, so that it can be saved to Json.

    Attributes
    ----------
    pts_list : list, compas.geometry.Point
    """

    data = {}
    for i in range(len(pts_list)):
        data[i] = list(pts_list[i])
    return data


#  --- Length of dictionary
def total_length_of_dictionary(dictionary):
    """
    Measures the total length of all the components of a dictionary

    Attributes
    ----------
    dictionary : dict

    Returns
    ----------
    float, total length of dictionary

    """

    total_length = 0
    for key in dictionary:
        total_length += len(dictionary[key])
    return total_length


#  --- Flattened list of dictionary
def flattened_list_of_dictionary(dictionary):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    flattened_list = []
    for key in dictionary:
        [flattened_list.append(item) for item in dictionary[key]]
    return flattened_list


def get_dict_key_from_value(dictionary, val):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    for key in dictionary:
        value = dictionary[key]
        if val == value:
            return key
    return "key doesn't exist"


#######################################
#  control flow

def interrupt():
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """

    value = input("Press enter to continue, Press 1 to abort ")
    print("")
    if isinstance(value, str):
        if value == '1':
            raise ValueError("Aborted")


#######################################
#  load all files with name

def get_all_files_with_name(startswith, endswith, DATA_PATH):
    files = []
    for file in os.listdir(DATA_PATH):
        if file.startswith(startswith) and file.endswith(endswith):
            files.append(file)
    print('')
    logger.info('Reloading : ' + str(files))
    return files


if __name__ == "__main__":
    pass
