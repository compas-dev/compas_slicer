import compas
from rdp import rdp
import numpy as np
from compas.geometry import Point



###################################
### Groups of print paths
###################################

class SortedPathCollection(object):
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


class Layer(SortedPathCollection):
    """
    Horizontal ordering. A Layer stores the print paths on a specific height level.
    """
    def __init__(self, contours, infill_paths, support_paths):
        SortedPathCollection.__init__(self, contours, infill_paths, support_paths) 


class Segment(SortedPathCollection):
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
            num+= len(isocurve.points)
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

    def simplify(self, threshold):
        reduced_pts = rdp(np.array(self.points), epsilon=threshold)
        self.points = [Point(v[0], v[1], v[2]) for v in reduced_pts] 

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