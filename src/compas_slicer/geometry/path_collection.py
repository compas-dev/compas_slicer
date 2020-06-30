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
    contours : list
        compas_slicer.geometry.Contour
    infills : list
        compas_slicer.geometry.InfillPath
    supports : list
        compas_slicer.geometry.SupportPath
    """

    def __init__(self, contours, infills, supports):
        # check input
        if contours:
            if len(contours) > 0:
                assert isinstance(contours[0], compas_slicer.geometry.Path)
        if infills:
            if len(infills) > 0:
                assert isinstance(infills[0], compas_slicer.geometry.Path)
        if supports:
            if len(supports) > 0:
                assert isinstance(supports[0], compas_slicer.geometry.Path)

        self.contours = contours
        self.infills = infills
        self.supports = supports

    def get_all_paths(self):
        all_paths = []
        [all_paths.append(path) for path in self.contours]
        if self.infills:
            [all_paths.append(path) for path in self.infills]
        if self.supports:
            [all_paths.append(path) for path in self.supports]
        return all_paths


class Layer(PathCollection):
    """
    Horizontal ordering. A Layer stores the print paths on a specific height level.
    """

    def __init__(self, contours, infill_paths, support_paths):
        PathCollection.__init__(self, contours, infill_paths, support_paths)


class Segment(PathCollection):
    """
    Vertical ordering. A Segment stores the print paths sorted in vertical groups.
    """

    def __init__(self, id):
        PathCollection.__init__(self, contours=[], infills=None, supports=None)
        self.id = id
        self.head_centroid = None

    def append_(self, contour):
        self.contours.append(contour)
        self.compute_head_centroid()

    def compute_head_centroid(self):
        ## Avoid using numpy for this
        self.head_centroid = utils.get_average_point(self.contours[-1].points)

    def total_number_of_points(self):
        num = 0
        for contour in self.contours:
            num += len(contour.printpoints)
        return num

    def printout_details(self):
        logger.info("Segment id : %d" % self.id)
        logger.info("Total number of contours : %d" % len(self.contours))
