import os
import json
import logging
import statistics

logger = logging.getLogger('logger')

__all__ = ['save_to_json',
           'load_from_json',
           'get_average_point',
           'length_of_flattened_dictionary']

def save_to_json(data, filepath, name):
    filename = os.path.join(filepath, name)
    logger.info("Saving to Json: " + filename)
    with open(filename, 'w') as f:
        f.write(json.dumps(data, indent=3, sort_keys=True))


def load_from_json(filepath, name):
    filename = os.path.join(filepath, name)
    with open(filename, 'r') as f:
        data = json.load(f)
    logger.info("Loaded Json: " + filename)
    return data


def get_average_point(points):
    x_mean = statistics.mean([p[0] for p in points])
    y_mean = statistics.mean([p[1] for p in points])
    z_mean = statistics.mean([p[2] for p in points])
    return [x_mean, y_mean, z_mean]

### --- Length of dictionary
def length_of_flattened_dictionary(dictionary):
    pass
#     total_length = 0
#     for key in dictionary:
#         a = dive_into(dictionary[key])
#         total_length += a
#         print('total_length : %d', total_length)
#     return total_length
#
#
# def dive_into(data):
#     if isinstance(dict, data):
#         for key in data:
#             dive_into(data[key])
#     else:
#         print('returning : %d', len(data))
#         return len(data)




def check_triangular_mesh(mesh):
    for f_key in mesh.faces():
        vs = mesh.face_vertices(f_key)
        if len(vs) != 3:
            raise TypeError("Found a quad at face key: " + str(f_key) + " ,number of face vertices:" + str(
                len(vs)) + ". \nOnly triangular meshes supported.")



if __name__ == "__main__":
    pass
