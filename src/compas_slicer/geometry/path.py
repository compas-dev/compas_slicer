from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from compas.data import Data
from compas.geometry import Point

__all__ = ["Path"]


@dataclass
class Path(Data):
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

    points: list[Point] = field(default_factory=list)
    is_closed: bool = False

    def __post_init__(self) -> None:
        super().__init__()  # Initialize Data base class
        if not self.points or not isinstance(self.points[0], Point):
            raise TypeError("points must be a non-empty list of compas.geometry.Point")

    def __repr__(self) -> str:
        no_of_points = len(self.points) if self.points else 0
        return f"<Path with {no_of_points} points>"

    @property
    def __data__(self) -> dict[str, Any]:
        return {
            "points": [point.__data__ for point in self.points],
            "is_closed": self.is_closed,
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> Path:
        points_data = data["points"]
        # Handle both list format and legacy dict format
        if isinstance(points_data, dict):
            pts = [
                Point.__from_data__(points_data[key])
                for key in sorted(points_data.keys(), key=lambda x: int(x))
            ]
        else:
            pts = [Point.__from_data__(p) for p in points_data]
        return cls(points=pts, is_closed=data["is_closed"])

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
        return cls.__from_data__(data)

    def to_data(self) -> dict[str, Any]:
        """Returns a dictionary of structured data representing the path.

        Returns
        -------
        dict
            The path's data.

        """
        return self.__data__
