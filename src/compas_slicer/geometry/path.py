import compas_slicer
import logging
import compas

logger = logging.getLogger('logger')

__all__ = ['Path']


class Path(object):
    """
    The Path class is the base class for all print paths.
    
    Attributes
    ----------
    points : list
        compas.geometry.Point
    is_closed : bool
    """

    def __init__(self, points, is_closed):
        ## check input
        assert isinstance(points[0], compas.geometry.Point)
        self.points = points  # class compas.geometry.Point
        self.is_closed = is_closed
        self.type = 'contour'  ## / 'infill' / 'support'

    def __repr__(self):
        no_of_points = len(self.points) if self.points else 0
        return "<Path object with %i points>" % (no_of_points)

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


if __name__ == '__main__':
    pass
