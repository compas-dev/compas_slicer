import os
import json

import logging

logger = logging.getLogger('logger')


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


if __name__ == "__main__":
    pass
