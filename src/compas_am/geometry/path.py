import compas_am
from compas_am.polyline_simplification import curvature_subsampling
import logging

logger = logging.getLogger('logger')

__all__ = ['PrintPath',
           'Contour',
           'Infill',
           'Support']


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
        assert isinstance(points[0], compas_am.geometry.PrintPoint)

        self.points = points  # Print point class
        for print_point in self.points:
            print_point.parent_path = self

        self.is_closed = is_closed

    ############################
    ### Polyline simplification

    def simplify_uniform(self, threshold):
        #TODO: THis function depends on the rdp library, should be moved elsewhere
        pass
        # import rdp
        # initial_points_number = len(self.points)
        # reduced_pts = rdp(np.array(self.points), epsilon=threshold)
        # self.points = [Point(point.pt[0], v[1], v[2]) for point in reduced_pts] 
        # logger.debug("Uniform subsampling: %d points removed"%(initial_points_number - len(self.points)))

    def simplify_adapted_to_curvature(self, threshold, iterations):
        initial_points_number = len(self.points)
        threshold = 3.3 / threshold  # Trying to make the same threshold have the same meaning for both simplification methods. Here as threshold goes down more points are removed, thus k/threshold to avoid confusion
        reduced_pts = curvature_subsampling(points=self.points, threshold=threshold, iterations=2)
        self.points = reduced_pts
        logger.debug("Curvature subsampling: %d points removed" % (initial_points_number - len(self.points)))

    ############################
    ### Output

    def get_lines_for_plotter(self, color=(255, 0, 0)):
        lines = []
        for i, point in enumerate(self.points):
            if self.is_closed:
                line = {
                    'start': point.pt,
                    'end': self.points[(i + 1) % (len(self.points) - 1)].pt,
                    'width': 1.0,
                    'color': color
                }
                lines.append(line)
            else:
                if i < len(self.points) - 1:
                    line = {
                        'start': point.pt,
                        'end': self.points[i + 1].pt,
                        'width': 1.0,
                        'color': color
                    }
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
