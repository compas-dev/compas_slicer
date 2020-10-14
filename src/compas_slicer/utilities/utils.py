import os
import json
import logging
import statistics

logger = logging.getLogger('logger')

__all__ = ['save_to_json',
           'load_from_json',
           'get_average_point',
           'total_length_of_dictionary',
           'flattened_list_of_dictionary',
           'interrupt',
           'point_list_to_dict']


def save_to_json(data, filepath, name):
    filename = os.path.join(filepath, name)
    logger.info("Saving to json: " + filename)
    with open(filename, 'w') as f:
        f.write(json.dumps(data, indent=3, sort_keys=True))


def load_from_json(filepath, name):
    filename = os.path.join(filepath, name)
    with open(filename, 'r') as f:
        data = json.load(f)
    logger.info("Loaded json: " + filename)
    return data


def get_average_point(points):
    x_mean = statistics.mean([p[0] for p in points])
    y_mean = statistics.mean([p[1] for p in points])
    z_mean = statistics.mean([p[2] for p in points])
    return [x_mean, y_mean, z_mean]


def check_triangular_mesh(mesh):
    for f_key in mesh.faces():
        vs = mesh.face_vertices(f_key)
        if len(vs) != 3:
            raise TypeError("Found a quad at face key: " + str(f_key) + " ,number of face vertices:" + str(
                len(vs)) + ". \nOnly triangular meshes supported.")


#######################################
#  dict utils
#######################################

def point_list_to_dict(pts_list):
    data = {}
    for i in range(len(pts_list)):
        data[i] = list(pts_list[i])
    return data


#  --- Length of dictionary
def total_length_of_dictionary(dictionary):
    total_length = 0
    for key in dictionary:
        total_length += len(dictionary[key])
    return total_length


#  --- Flattened list of dictionary
def flattened_list_of_dictionary(dictionary):
    flattened_list = []
    for key in dictionary:
        [flattened_list.append(item) for item in dictionary[key]]
    return flattened_list


#######################################
#  control flow
#######################################

def interrupt():
    value = input("Press enter to continue, Press 1 to abort ")
    print("")
    if isinstance(value, str):
        if value == '1':
            raise ValueError("Aborted")


if __name__ == "__main__":
    pass
