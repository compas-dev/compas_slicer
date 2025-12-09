from __future__ import annotations

from typing import Any

from compas.geometry import Frame, Point, Vector, cross_vectors, dot_vectors, norm_vector

import compas_slicer.utilities.utils as utils

__all__ = ["PrintPoint"]


class PrintPoint:
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

    def __init__(self, pt: Point, layer_height: float, mesh_normal: Vector) -> None:
        if not isinstance(pt, Point):
            raise TypeError("pt must be a compas.geometry.Point")
        if not isinstance(mesh_normal, Vector):
            raise TypeError("mesh_normal must be a compas.geometry.Vector")
        if not layer_height:
            raise ValueError("layer_height must be provided")

        self.pt = pt
        self.layer_height = layer_height
        self.mesh_normal = mesh_normal
        self.up_vector = Vector(0, 0, 1)
        self.frame = self.get_frame()

        # Attributes transferred from mesh
        self.attributes: dict[str, Any] = {}

        # Print organization attributes
        self.extruder_toggle: bool | None = None
        self.velocity: float | None = None
        self.wait_time: float | None = None
        self.blend_radius: float | None = None

        # Support relation
        self.closest_support_pt: Point | None = None
        self.distance_to_support: float | None = None

        self.is_feasible = True

    def __repr__(self) -> str:
        x, y, z = self.pt[0], self.pt[1], self.pt[2]
        return f"<PrintPoint object at ({x:.2f}, {y:.2f}, {z:.2f})>"

    def get_frame(self) -> Frame:
        """Returns a Frame with x-axis pointing up, y-axis towards mesh normal."""
        if abs(dot_vectors(self.up_vector, self.mesh_normal)) < 1.0:
            c = cross_vectors(self.up_vector, self.mesh_normal)
            if norm_vector(c) == 0:
                c = Vector(1, 0, 0)
            if norm_vector(self.mesh_normal) == 0:
                self.mesh_normal = Vector(0, 1, 0)
            return Frame(self.pt, c, self.mesh_normal)
        else:
            return Frame(self.pt, Vector(1, 0, 0), Vector(0, 1, 0))

    def to_data(self) -> dict[str, Any]:
        """Returns a dictionary of structured data representing the PrintPoint.

        Returns
        -------
        dict
            The PrintPoint's data.

        """
        return {
            "point": [self.pt[0], self.pt[1], self.pt[2]],
            "layer_height": self.layer_height,
            "mesh_normal": self.mesh_normal.to_data(),
            "up_vector": self.up_vector.to_data(),
            "frame": self.frame.to_data(),
            "extruder_toggle": self.extruder_toggle,
            "velocity": self.velocity,
            "wait_time": self.wait_time,
            "blend_radius": self.blend_radius,
            "closest_support_pt": self.closest_support_pt.to_data() if self.closest_support_pt else None,
            "distance_to_support": self.distance_to_support,
            "is_feasible": self.is_feasible,
            "attributes": utils.get_jsonable_attributes(self.attributes),
        }

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
        pp = cls(
            pt=Point.from_data(data["point"]),
            layer_height=data["layer_height"],
            mesh_normal=Vector.from_data(data["mesh_normal"]),
        )

        pp.up_vector = Vector.from_data(data["up_vector"])
        pp.frame = Frame.from_data(data["frame"])

        pp.extruder_toggle = data["extruder_toggle"]
        pp.velocity = data["velocity"]
        pp.wait_time = data["wait_time"]
        pp.blend_radius = data["blend_radius"]

        if data["closest_support_pt"]:
            pp.closest_support_pt = Point.from_data(data["closest_support_pt"])
        pp.distance_to_support = data["distance_to_support"]

        pp.is_feasible = data["is_feasible"]
        pp.attributes = data["attributes"]

        return pp
