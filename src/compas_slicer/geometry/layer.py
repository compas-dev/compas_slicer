import logging
import compas_slicer
import compas_slicer.utilities as utils
from compas_slicer.geometry import Path

logger = logging.getLogger('logger')

__all__ = ['Layer',
           'VerticalLayer']


class Layer(object):
    """
    A Layer stores a group of ordered print_paths.

    Attributes
    ----------
    paths : list
        compas_slicer.geometry.Path
    """

    def __init__(self, paths):
        # check input
        if len(paths) > 0:
            assert isinstance(paths[0], compas_slicer.geometry.Path)
        self.paths = paths

    def __repr__(self):
        no_of_paths = len(self.paths) if self.paths else 0
        return "<Layer object with %i paths>" % no_of_paths

    @classmethod
    def from_data(cls, data):
        paths = [Path.from_data(data[key]) for key in data]
        layer = cls(paths=paths)
        return layer

    def to_data(self):
        data = {}
        for i, path in enumerate(self.paths):
            data[i] = path.to_data()
        return data

class VerticalLayer(Layer):
    """
    Vertical ordering. A VerticalLayer stores the print paths sorted in vertical groups.
    """

    def __init__(self, id):
        Layer.__init__(self, paths=[])
        self.id = id
        self.head_centroid = None

    def append_(self, path):
        self.paths.append(path)
        self.compute_head_centroid()

    def compute_head_centroid(self):
        ## Avoid using numpy for this
        self.head_centroid = utils.get_average_point(self.paths[-1].points)

    def total_number_of_points(self):
        num = 0
        for path in self.paths:
            num += len(path.printpoints)
        return num

    def printout_details(self):
        logger.info("VerticalLayer id : %d" % self.id)
        logger.info("Total number of paths : %d" % len(self.paths))
