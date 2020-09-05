import logging
import compas_slicer
import compas_slicer.utilities as utils

logger = logging.getLogger('logger')

__all__ = ['PathCollection',
           'Layer',
           'Segment']

class PathCollection(object):
    """
    A PathCollection stores a group of ordered print_paths

    Attributes
    ----------
    paths : list
        compas_slicer.geometry.Path
    """

    def __init__(self, paths):
        # check input
        if len(paths)>0:
            assert isinstance(paths[0], compas_slicer.geometry.Path)
        self.paths = paths


class Layer(PathCollection):
    """
    Horizontal ordering. A Layer stores the print paths on a specific height level.
    """
    def __init__(self, paths):
        PathCollection.__init__(self, paths)

class Segment(PathCollection):
    """
    Vertical ordering. A Segment stores the print paths sorted in vertical groups.
    """

    def __init__(self, id):
        PathCollection.__init__(self, paths=[])
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
        logger.info("Segment id : %d" % self.id)
        logger.info("Total number of paths : %d" % len(self.paths))
