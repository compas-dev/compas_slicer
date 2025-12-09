from __future__ import annotations

import logging
from typing import Any

from compas.geometry import Point

logger = logging.getLogger("logger")

__all__ = ["Path"]


class Path:
    """A Path is a connected contour within a Layer.

    A Path consists of a list of compas.geometry.Points.

    Attributes
    ----------
    points : list[Point]
        List of points defining the path.
    is_closed : bool
        True if the Path is a closed curve, False if the Path is open.
        If the path is closed, the first and the last point are identical.

    """

    def __init__(self, points: list[Point], is_closed: bool) -> None:
        if not points or not isinstance(points[0], Point):
            raise TypeError("points must be a non-empty list of compas.geometry.Point")

        self.points = points
        self.is_closed = is_closed

    def __repr__(self) -> str:
        no_of_points = len(self.points) if self.points else 0
        return f"<Path object with {no_of_points} points>"

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> Path:
        """Construct a path from its data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        Path
            The constructed path.

        """
        points_data = data["points"]
        pts = [
            Point(points_data[key][0], points_data[key][1], points_data[key][2])
            for key in points_data
        ]
        return cls(points=pts, is_closed=data["is_closed"])

    def to_data(self) -> dict[str, Any]:
        """Returns a dictionary of structured data representing the path.

        Returns
        -------
        dict
            The path's data.

        """
        return {
            "points": {i: point.__data__ for i, point in enumerate(self.points)},
            "is_closed": self.is_closed,
        }
