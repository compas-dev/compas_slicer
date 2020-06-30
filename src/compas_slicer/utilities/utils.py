import os
import json
import logging
import statistics

logger = logging.getLogger('logger')

__all__ = ['save_to_json',
           'load_from_json',
           'get_average_point']

def save_to_json(data, path, name):
    filename = os.path.join(path, name)
    logger.info("Saving to Json: " + filename)
    with open(filename, 'w') as f:
        f.write(json.dumps(data, indent=3, sort_keys=True))


def load_from_json(path, name):
    filename = os.path.join(path, name)
    with open(filename, 'r') as f:
        data = json.load(f)
    logger.info("Loaded Json: " + filename)
    return data


def get_average_point(points):
    x_mean = statistics.mean([p[0] for p in points])
    y_mean = statistics.mean([p[1] for p in points])
    z_mean = statistics.mean([p[2] for p in points])
    return [x_mean, y_mean, z_mean]

if __name__ == "__main__":
    pass
