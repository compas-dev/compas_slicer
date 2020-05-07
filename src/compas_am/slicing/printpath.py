import compas
from rdp import rdp
import numpy as np
from compas.geometry import Point

class PrintPath(object):
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


##########################

class Layer(object):
    def __init__(self, contours, infill_path, support_path):
        self.contours = contours
        self.infill_path = infill_path
        self.support_path = support_path

########

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