from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from compas.data import Data
from compas.geometry import Frame, Point, Vector, cross_vectors, dot_vectors, norm_vector

import compas_slicer.utilities.utils as utils

__all__ = ["PrintPoint"]


@dataclass
class PrintPoint(Data):
    """A PrintPoint consists of a compas.geometry.Point and printing attributes.

    Attributes
    ----------
    pt : Point
        A compas Point consisting of x, y, z coordinates.
    layer_height : float
        The distance between the point on this layer and the previous layer.
    mesh_normal : Vector
        Normal of the mesh at this PrintPoint.
    up_vector : Vector
        Vector in up direction.
    frame : Frame
        Frame with x-axis pointing up, y-axis pointing towards the mesh normal.
    extruder_toggle : bool | None
        True if extruder should be on, False if off.
    velocity : float | None
        Velocity for printing (print speed), in mm/s.
    wait_time : float | None
        Time in seconds to wait at this PrintPoint.
    blend_radius : float | None
        Blend radius in mm.
    closest_support_pt : Point | None
        Closest support point.
    distance_to_support : float | None
        Distance to support.
    is_feasible : bool
        Whether this print point is feasible.
    attributes : dict[str, Any]
        Additional attributes transferred from the mesh.

    """

    pt: Point
    layer_height: float
    mesh_normal: Vector
    up_vector: Vector = field(default_factory=lambda: Vector(0, 0, 1))
    frame: Frame | None = field(default=None)
    extruder_toggle: bool | None = None
    velocity: float | None = None
    wait_time: float | None = None
    blend_radius: float | None = None
    closest_support_pt: Point | None = None
    distance_to_support: float | None = None
    is_feasible: bool = True
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__init__()  # Initialize Data base class
        if not isinstance(self.pt, Point):
            raise TypeError("pt must be a compas.geometry.Point")
        if not isinstance(self.mesh_normal, Vector):
            raise TypeError("mesh_normal must be a compas.geometry.Vector")
        if not self.layer_height:
            raise ValueError("layer_height must be provided")
        if self.frame is None:
            self.frame = self._compute_frame()

    def __repr__(self) -> str:
        x, y, z = self.pt[0], self.pt[1], self.pt[2]
        return f"<PrintPoint at ({x:.2f}, {y:.2f}, {z:.2f})>"

    def _compute_frame(self) -> Frame:
        """Compute frame with x-axis pointing up, y-axis towards mesh normal."""
        if abs(dot_vectors(self.up_vector, self.mesh_normal)) < 1.0:
            c = cross_vectors(self.up_vector, self.mesh_normal)
            if norm_vector(c) == 0:
                c = Vector(1, 0, 0)
            mesh_normal = self.mesh_normal
            if norm_vector(mesh_normal) == 0:
                mesh_normal = Vector(0, 1, 0)
            return Frame(self.pt, c, mesh_normal)
        else:
            return Frame(self.pt, Vector(1, 0, 0), Vector(0, 1, 0))

    def get_frame(self) -> Frame:
        """Returns a Frame with x-axis pointing up, y-axis towards mesh normal."""
        return self._compute_frame()

    @property
    def __data__(self) -> dict[str, Any]:
        return {
            "pt": self.pt.__data__,
            "layer_height": self.layer_height,
            "mesh_normal": self.mesh_normal.__data__,
            "up_vector": self.up_vector.__data__,
            "frame": self.frame.__data__ if self.frame else None,
            "extruder_toggle": self.extruder_toggle,
            "velocity": self.velocity,
            "wait_time": self.wait_time,
            "blend_radius": self.blend_radius,
            "closest_support_pt": self.closest_support_pt.__data__ if self.closest_support_pt else None,
            "distance_to_support": self.distance_to_support,
            "is_feasible": self.is_feasible,
            "attributes": utils.get_jsonable_attributes(self.attributes),
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> PrintPoint:
        closest_support_pt = None
        if data.get("closest_support_pt"):
            closest_support_pt = Point.__from_data__(data["closest_support_pt"])

        frame: Frame | None = None
        if data.get("frame"):
            frame = Frame.__from_data__(data["frame"])  # type: ignore[assignment]

        return cls(
            pt=Point.__from_data__(data["pt"]),
            layer_height=data["layer_height"],
            mesh_normal=Vector.__from_data__(data["mesh_normal"]),
            up_vector=Vector.__from_data__(data["up_vector"]),
            frame=frame,
            extruder_toggle=data.get("extruder_toggle"),
            velocity=data.get("velocity"),
            wait_time=data.get("wait_time"),
            blend_radius=data.get("blend_radius"),
            closest_support_pt=closest_support_pt,
            distance_to_support=data.get("distance_to_support"),
            is_feasible=data.get("is_feasible", True),
            attributes=data.get("attributes", {}),
        )

    def to_data(self) -> dict[str, Any]:
        """Returns a dictionary of structured data representing the PrintPoint.

        Returns
        -------
        dict
            The PrintPoint's data.

        """
        return self.__data__

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> PrintPoint:
        """Construct a PrintPoint from its data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        PrintPoint
            The constructed PrintPoint.

        """
        # Handle legacy format with "point" key instead of "pt"
        if "point" in data and "pt" not in data:
            data["pt"] = data.pop("point")
        return cls.__from_data__(data)
