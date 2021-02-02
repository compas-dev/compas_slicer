import logging
import compas
from compas.geometry import Point

logger = logging.getLogger('logger')

__all__ = ['Path']


class Path(object):
    """
    A Path is a connected contour within a Layer. A Path consists of a list of
    compas.geometry.Points.

    Attributes
    ----------
    points: list
        :class:`compas.geometry.Point`
    is_closed: bool
        True if the Path is a closed curve, False if the Path is open.
        If the path is closed, the first and the last point are identical.
    """

    def __init__(self, points, is_closed):
        # check input
        assert isinstance(points[0], compas.geometry.Point)

        self.points = points  # :class: compas.geometry.Point
        self.is_closed = is_closed  # bool

    def __repr__(self):
        no_of_points = len(self.points) if self.points else 0
        return "<Path object with %i points>" % no_of_points

    @classmethod
    def from_data(cls, data):
        """Construct a path from its data representation.

        Parameters
        ----------
        data: dict
            The data dictionary.

        Returns
        -------
        path
            The constructed path.

        """
        points_data = data['points']
        pts = [Point(points_data[key][0], points_data[key][1], points_data[key][2])
               for key in points_data]
        path = cls(points=pts, is_closed=data['is_closed'])
        return path

    def to_data(self):
        """Returns a dictionary of structured data representing the data structure.

        Returns
        -------
        dict
            The path's data.

        """
        data = {'points': {i: point.to_data() for i, point in enumerate(self.points)},
                'is_closed': self.is_closed}
        return data


if __name__ == '__main__':
    pass
