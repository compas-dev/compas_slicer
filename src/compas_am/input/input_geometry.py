from compas.datastructures import Mesh

import logging

logger = logging.getLogger('logger')

__all__ = ['InputGeometry']

class InputGeometry:
    def __init__(self, filepath):
        self.mesh = self.load_mesh(filepath)

    def load_mesh(self, filepath):
        if str(filepath)[-4:] == '.stl':
            return Mesh.from_stl(filepath)
        elif str(filepath)[-4:] == '.obj':
            return Mesh.from_obj(filepath)
        elif str(filepath)[-4:] == 'json':
            return Mesh.from_json(filepath)
        else:
            logger.error("Cannot import files : " + str(filepath)[-3:])


if __name__ == "__main__":
    pass
