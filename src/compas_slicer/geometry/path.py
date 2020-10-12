import compas_slicer
import logging
import compas
from compas.geometry import Point

logger = logging.getLogger('logger')

__all__ = ['Path']


class Path(object):
    """
    The Path class is the base class for all print paths.
    It consists out of a list of compas Points.
    
    Attributes
    ----------
    points : list
        compas.geometry.Point
    is_closed : bool
        ...
    type : string
        Stores whether the Path is a contour, infill or support.
        Currently only contour is available.
    """

    def __init__(self, points, is_closed):
        ## check input
        assert isinstance(points[0], compas.geometry.Point)
        self.points = points  # class compas.geometry.Point
        self.is_closed = is_closed

    def __repr__(self):
        no_of_points = len(self.points) if self.points else 0
        return "<Path object with %i points>" % (no_of_points)

    @classmethod
    def from_data(cls, data):
        pts = [Point(p[0], p[1], p[2])for p in data['points']]
        path = cls(points=pts, is_closed=data['is_closed'])
        return path

    def to_data(self):
        data = {'points': {},
                'is_closed': self.is_closed}
        for i, point in enumerate(self.points):
            data['points'][i] = [point[0], point[1], point[2]]
        return data


if __name__ == '__main__':
    pass
