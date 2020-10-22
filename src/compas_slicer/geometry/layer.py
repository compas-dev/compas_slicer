import logging
import compas_slicer
import numpy as np
from compas_slicer.geometry import Path

logger = logging.getLogger('logger')

__all__ = ['Layer',
           'VerticalLayer']


class Layer(object):
    """
    A Layer stores a group of ordered print_paths.

    A Layer is generated when a geometry is sliced into layers and can therefore be 
    seen as a 'slice' of a geometry. Layers are typically organized horizontally, 
    but can also be organized vertically. A Layer consists out of one, or multiple
    Paths (depending on the geometry). 

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
        pts = np.array(self.paths[-1].points)
        self.head_centroid = np.mean(pts, axis=0)

    def total_number_of_points(self):
        num = 0
        for path in self.paths:
            num += len(path.printpoints)
        return num

    def printout_details(self):
        logger.info("VerticalLayer id : %d" % self.id)
        logger.info("Total number of paths : %d" % len(self.paths))
