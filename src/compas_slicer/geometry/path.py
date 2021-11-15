import logging
import compas
from compas.geometry import Point

logger = logging.getLogger('logger')

__all__ = ['ContourPath',
           'InfillPath',
           'TravelPath',
           'Path']


###################
# ContourPath
###################

class ContourPath(object):
    """ A Path is a connected contour within a Layer, that is the direct result of the slicing process.

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
        assert len(points) > 1
        assert isinstance(points[0], compas.geometry.Point)

        self.points = points  # list of :class: compas.geometry.Point
        self.is_closed = is_closed  # bool

    def __repr__(self):
        no_of_points = len(self.points) if self.points else 0
        return "<ContourPath with %i points>" % no_of_points

    @classmethod
    def from_data(cls, data):
        """ Construct a path from its data representation.
        Parameters
        ----------
        data: dict, the data dictionary.

        Returns
        -------
        path: The constructed path.
        """
        points_data = data['points']
        pts = [Point(points_data[key][0], points_data[key][1], points_data[key][2])
               for key in points_data]
        path = cls(points=pts, is_closed=data['is_closed'])
        return path

    def to_data(self):
        """ Returns a dictionary of structured data representing the data structure.
        Returns
        -------
        dict: The path's data.
        """
        data = {'points': {i: point.to_data() for i, point in enumerate(self.points)},
                'is_closed': self.is_closed}
        return data


###################
# InfillPath
###################

class InfillPath(object):
    def __init__(self, points):
        assert len(points) > 1
        assert isinstance(points[0], compas.geometry.Point)
        self.points = points  # list of :class: compas.geometry.Point

    def __repr__(self):
        no_of_points = len(self.points) if self.points else 0
        return "<InfillPath with %i points>" % no_of_points

    @classmethod
    def from_data(cls, data):
        points_data = data['points']
        pts = [Point(points_data[key][0], points_data[key][1], points_data[key][2])
               for key in points_data]
        path = cls(points=pts)
        return path

    def to_data(self):
        data = {'points': {i: point.to_data() for i, point in enumerate(self.points)}}
        return data


###################
# TravelPath
###################

class TravelPath(object):
    def __init__(self, points):
        assert len(points) > 1
        assert isinstance(points[0], compas.geometry.Point)
        self.points = points  # list of :class: compas.geometry.Point

    def __repr__(self):
        no_of_points = len(self.points) if self.points else 0
        return "<TravelPath with %i points>" % no_of_points

    @classmethod
    def from_data(cls, data):
        points_data = data['points']
        pts = [Point(points_data[key][0], points_data[key][1], points_data[key][2])
               for key in points_data]
        path = cls(points=pts)
        return path

    def to_data(self):
        data = {'points': {i: point.to_data() for i, point in enumerate(self.points)}}
        return data


###################
# Path
###################

class Path(object):
    """
    A Path the overarching class that contains the paths of all the above types
    """

    def __init__(self, contour):
        self.contour = contour

        self.travel_to_contour = None  # optional
        self.travel_to_infill = None  # optional
        self.infill = None  # optional

    def __repr__(self):
        return "<Path object >"

    def get_existing_path_types(self):
        existing_types = ['contour']
        if self.travel_to_contour:
            existing_types.append('travel_to_contour')
        if self.travel_to_infill:
            existing_types.append('travel_to_infill')
        if self.infill:
            existing_types.append('infill')
        return existing_types

    def number_of_points(self):
        n = 0
        if self.travel_to_contour:
            n += len(self.travel_to_contour.points)
        n += len(self.contour.points)
        if self.travel_to_infill:
            n += len(self.travel_to_infill.points)
        if self.infill:
            n += len(self.infill.points)
        return n

    @classmethod
    def from_data(cls, data):
        contour = ContourPath.from_data(data['contour'])
        if data['travel_to_contour']:
            travel_to_contour = TravelPath.from_data(data['travel_to_contour'])
        else:
            travel_to_contour = None
        if data['travel_to_infill']:
            travel_to_infill = TravelPath.from_data(data['travel_to_infill'])
        else:
            travel_to_infill = None
        if data['infill']:
            infill = InfillPath.from_data(data['infill'])
        else:
            infill = None

        path = cls(contour)
        path.travel_to_contour = travel_to_contour
        path.travel_to_infill = travel_to_infill
        path.infill = infill
        return path

    def to_data(self):
        data = {'contour': self.contour.to_data(),
                'travel_to_contour': self.travel_to_contour.to_data() if self.travel_to_contour else None,
                'travel_to_infill': self.travel_to_infill.to_data() if self.travel_to_infill else None,
                'infill': self.infill.to_data() if self.infill else None}
        return data


if __name__ == '__main__':
    pass
