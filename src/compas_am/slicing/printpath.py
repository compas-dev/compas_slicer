import compas
from rdp import rdp
import numpy as np
from compas.geometry import Point

import compas_am
from compas_am.polyline_simplification.curvature_subsampling import curvature_subsampling
from compas_am.slicing.print_point import PrintPoint

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
    infills : list
        compas_am.slicing.printpath.InfillPath
    supports : list 
        compas_am.slicing.printpath.SupportPath>
    """
    def __init__(self, contours, infills, supports):
        # check input
        assert isinstance(contours[0], compas_am.slicing.printpath.PrintPath)
        if infills:
            assert isinstance(infills[0], compas_am.slicing.printpath.PrintPath)
        if infills:
            assert isinstance(supports[0], compas_am.slicing.printpath.PrintPath)

        self.contours = contours
        self.infills = infills
        self.supports = supports

    def get_all_paths(self):
        all_paths = []
        [all_paths.append(path) for path in self.contours]
        if self.infills:
            [all_paths.append(path) for path in self.infill_paths]
        if self.supports:
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
        self.infills = []
        self.supports = []

    def append_(self, contour):
        self.contours.append(contour)
        self.compute_head_centroid()

    def compute_head_centroid(self):
        last_layer_pts = np.array([point.pt for point in self.contours[-1].points])
        self.head_centroid = np.mean(last_layer_pts, axis=0)

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
        # check input
        assert isinstance(points[0], compas_am.slicing.print_point.PrintPoint)

        self.points = points # Print point class
        for print_point in self.points:
            print_point.parent_path = self 

        self.is_closed = is_closed

    ############################
    ### Polyline simplification

    def simplify_uniform(self, threshold):
        pass
        # initial_points_number = len(self.points)
        # reduced_pts = rdp(np.array(self.points), epsilon=threshold)
        # self.points = [Point(point.pt[0], v[1], v[2]) for point in reduced_pts] 
        # logger.debug("Uniform subsampling: %d points removed"%(initial_points_number - len(self.points)))

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
        for i, point in enumerate(self.points):
            if self.is_closed:
                line = {}
                line['start'] = point.pt
                line['end'] = self.points[(i+1)%(len(self.points) -1)].pt
                line['width'] = 1.0
                line['color'] = color
                lines.append(line)
            else: 
                if i<len(self.points) -1:
                    line = {}
                    line['start'] = point.pt
                    line['end'] = self.points[i+1].pt
                    line['width'] = 1.0
                    line['color'] = color
                    lines.append(line)
        return lines

class Contour(PrintPath):
    def __init__(self, points, is_closed):
        PrintPath.__init__(self, points, is_closed) 

class Infill(PrintPath):
    def __init__(self, points, is_closed):
        PrintPath.__init__(self, points, is_closed)        

class Support(PrintPath):
    def __init__(self, points, is_closed):
        PrintPath.__init__(self, points, is_closed) 


if __name__ == '__main__':
    pass