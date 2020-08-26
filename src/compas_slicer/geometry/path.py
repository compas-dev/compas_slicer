import compas_slicer
import logging

logger = logging.getLogger('logger')

__all__ = ['Path',
           'Contour',
           'Infill',
           'Support']


class Path(object):
    """
    The Path class is the base class for all print paths.
    
    Attributes
    ----------
    points : list
        compas.geometry.Point
    is_closed : bool
    """
    def __init__(self, printpoints, is_closed):
        self.points = None

        # check input
        # assert isinstance(points[0], compas_slicer.geometry.PrintPoint)

        self.printpoints = printpoints  # PrintPoint class
        # for print_point in self.printpoints:
        #     print_point.parent_path = self

        self.is_closed = is_closed

    ############################
    ### Output

    def get_lines_for_plotter(self, color=(255, 0, 0)):
        lines = []
        for i, point in enumerate(self.points):
            if self.is_closed:
                line = {
                    'start': point,
                    'end': self.points[(i + 1) % (len(self.points) - 1)],
                    'width': 1.0,
                    'color': color
                }
                lines.append(line)
            else:
                if i < len(self.points) - 1:
                    line = {
                        'start': point,
                        'end': self.points[i + 1],
                        'width': 1.0,
                        'color': color
                    }
                    lines.append(line)
        return lines


class Contour(Path):
    def __init__(self, points, is_closed):
        Path.__init__(self, points, is_closed)


class Infill(Path):
    def __init__(self, points, is_closed):
        Path.__init__(self, points, is_closed)


class Support(Path):
    def __init__(self, points, is_closed):
        Path.__init__(self, points, is_closed)


if __name__ == '__main__':
    pass
