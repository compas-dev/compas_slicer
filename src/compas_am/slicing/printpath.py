import compas
from rdp import rdp
import numpy as np
from compas.geometry import Point

from compas_am.polyline_simplification.curvature_subsampling import curvature_subsampling

import logging
logger = logging.getLogger('logger')

###################################
### Groups of print paths
###################################

class PathCollection(object):
    """
    A Layer stores the print paths on a specific height level.
    
    Attributes
    ----------
    contours : list
        compas_am.slicing.printpath.Contour
    infill_paths : list
        compas_am.slicing.printpath.InfillPath
    support_paths : list 
        compas_am.slicing.printpath.SupportPath>
    """
    def __init__(self, contours, infill_paths, support_paths):
        self.contours = contours
        self.infill_paths = infill_paths
        self.support_paths = support_paths

    def get_all_paths(self):
        all_paths = []
        [all_paths.append(path) for path in self.contours]
        if self.infill_paths:
            [all_paths.append(path) for path in self.infill_paths]
        if self.support_paths:
            [all_paths.append(path) for path in self.support_paths]
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
        self.id = id
        self.head_centroid = None

        self.contours = []
        self.infill_paths = []
        self.support_paths = []

    def append_(self, contour):
        self.contours.append(contour)
        self.compute_head_centroid()

    def compute_head_centroid(self):
        pts = np.array(self.contours[-1].points)
        self.head_centroid = np.mean(pts, axis=0)

    def total_number_of_points(self):
        num = 0
        for contour in self.contours:
            num+= len(contour.points)
        return num

    def printout_details(self):
        logger.info("Segment id : %d"%self.id)
        logger.info("Total number of contours : %d"%len(self.contours))




###################################
### Print paths
###################################

class PrintPath(object):
    """
    The PrintPath class is the base class for all print paths.
    
    Attributes
    ----------
    points : list
        compas.geometry.Point
    is_closed : bool
    """
    def __init__(self, points, is_closed):
        self.points = points
        self.is_closed = is_closed

    ############################
    ### Polyline simplification

    def simplify_uniform(self, threshold):
        initial_points_number = len(self.points)
        reduced_pts = rdp(np.array(self.points), epsilon=threshold)
        self.points = [Point(v[0], v[1], v[2]) for v in reduced_pts] 
        logger.debug("Uniform subsampling: %d points removed"%(initial_points_number - len(self.points)))

    def simplify_adapted_to_curvature(self, threshold, iterations):
        initial_points_number = len(self.points)
        threshold = 3.3 / threshold #Trying to make the same threshold have the same meaning for both simplification methods. Here as threshold goes down more points are removed, thus k/threshold to avoid confusion 
        reduced_pts = curvature_subsampling(points = self.points, threshold = threshold, iterations = 2)
        self.points = reduced_pts
        logger.debug("Curvature subsampling: %d points removed"%(initial_points_number - len(self.points)))

    ############################
    ### Output

    def get_lines_for_plotter(self, color = (255,0,0)):
        lines = []
        for i, pt in enumerate(self.points):
            if self.is_closed:
                line = {}
                line['start'] = pt
                line['end'] = self.points[(i+1)%(len(self.points) -1)]
                line['width'] = 1.0
                line['color'] = color
                lines.append(line)
            else: 
                if i<len(self.points) -1:
                    line = {}
                    line['start'] = pt
                    line['end'] = self.points[i+1]
                    line['width'] = 1.0
                    line['color'] = color
                    lines.append(line)
        return lines

class Contour(PrintPath):
    def __init__(self, points, is_closed):
        PrintPath.__init__(self, points, is_closed) 

class InfillPath(PrintPath):
    def __init__(self, points, is_closed):
        PrintPath.__init__(self, points, is_closed)        

class SupportPath(PrintPath):
    def __init__(self, points, is_closed):
        PrintPath.__init__(self, points, is_closed) 


if __name__ == '__main__':
    pass