from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from compas.data import Data

__all__ = ["GcodeParameters"]


@dataclass
class GcodeParameters(Data):
    """Parameters for G-code generation.

    Attributes
    ----------
    nozzle_diameter : float
        Nozzle diameter in mm.
    filament_diameter : float
        Filament diameter in mm, for calculating E.
    delta : bool
        True for delta printers.
    print_volume_x : float
        Print volume X dimension in mm.
    print_volume_y : float
        Print volume Y dimension in mm.
    print_volume_z : float
        Print volume Z dimension in mm.
    layer_width : float
        Layer width in mm.
    extruder_temperature : int
        Extruder temperature in °C.
    bed_temperature : int
        Bed temperature in °C.
    fan_speed : int
        Fan speed (0-255).
    fan_start_z : float
        Height at which the fan starts in mm.
    flowrate : float
        Global flow multiplier as fraction.
    feedrate : float
        Print feedrate in mm/min.
    feedrate_travel : float
        Travel feedrate in mm/min.
    feedrate_low : float
        Low feedrate in mm/min.
    feedrate_retraction : float
        Retraction feedrate in mm/min.
    acceleration : float
        Acceleration in mm/s². If 0, uses driver default.
    jerk : float
        Jerk in mm/s. If 0, uses driver default.
    z_hop : float
        Z hop distance in mm.
    retraction_length : float
        Retraction length in mm.
    retraction_min_travel : float
        Minimum travel for retraction in mm.
    flow_over : float
        Overextrusion factor for z < min_over_z.
    min_over_z : float
        Height below which overextrusion applies in mm.

    """

    def __post_init__(self) -> None:
        super().__init__()  # Initialize Data base class

    # Physical parameters
    nozzle_diameter: float = 0.4
    filament_diameter: float = 1.75
    delta: bool = False
    print_volume_x: float = 300.0
    print_volume_y: float = 300.0
    print_volume_z: float = 600.0

    # Dimensional parameters
    layer_width: float = 0.6

    # Temperature parameters
    extruder_temperature: int = 200
    bed_temperature: int = 60
    fan_speed: int = 255
    fan_start_z: float = 0.0

    # Movement parameters
    flowrate: float = 1.0
    feedrate: float = 3600.0
    feedrate_travel: float = 4800.0
    feedrate_low: float = 1800.0
    feedrate_retraction: float = 2400.0
    acceleration: float = 0.0
    jerk: float = 0.0

    # Retraction
    z_hop: float = 0.5
    retraction_length: float = 1.0
    retraction_min_travel: float = 6.0

    # Adhesion parameters
    flow_over: float = 1.0
    min_over_z: float = 0.0

    @property
    def __data__(self) -> dict[str, Any]:
        return {
            "nozzle_diameter": self.nozzle_diameter,
            "filament_diameter": self.filament_diameter,
            "delta": self.delta,
            "print_volume_x": self.print_volume_x,
            "print_volume_y": self.print_volume_y,
            "print_volume_z": self.print_volume_z,
            "layer_width": self.layer_width,
            "extruder_temperature": self.extruder_temperature,
            "bed_temperature": self.bed_temperature,
            "fan_speed": self.fan_speed,
            "fan_start_z": self.fan_start_z,
            "flowrate": self.flowrate,
            "feedrate": self.feedrate,
            "feedrate_travel": self.feedrate_travel,
            "feedrate_low": self.feedrate_low,
            "feedrate_retraction": self.feedrate_retraction,
            "acceleration": self.acceleration,
            "jerk": self.jerk,
            "z_hop": self.z_hop,
            "retraction_length": self.retraction_length,
            "retraction_min_travel": self.retraction_min_travel,
            "flow_over": self.flow_over,
            "min_over_z": self.min_over_z,
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> GcodeParameters:
        return cls(
            nozzle_diameter=data.get("nozzle_diameter", 0.4),
            filament_diameter=data.get("filament_diameter", 1.75),
            delta=data.get("delta", False),
            print_volume_x=data.get("print_volume_x", 300.0),
            print_volume_y=data.get("print_volume_y", 300.0),
            print_volume_z=data.get("print_volume_z", 600.0),
            layer_width=data.get("layer_width", 0.6),
            extruder_temperature=data.get("extruder_temperature", 200),
            bed_temperature=data.get("bed_temperature", 60),
            fan_speed=data.get("fan_speed", 255),
            fan_start_z=data.get("fan_start_z", 0.0),
            flowrate=data.get("flowrate", 1.0),
            feedrate=data.get("feedrate", 3600.0),
            feedrate_travel=data.get("feedrate_travel", 4800.0),
            feedrate_low=data.get("feedrate_low", 1800.0),
            feedrate_retraction=data.get("feedrate_retraction", 2400.0),
            acceleration=data.get("acceleration", 0.0),
            jerk=data.get("jerk", 0.0),
            z_hop=data.get("z_hop", 0.5),
            retraction_length=data.get("retraction_length", 1.0),
            retraction_min_travel=data.get("retraction_min_travel", 6.0),
            flow_over=data.get("flow_over", 1.0),
            min_over_z=data.get("min_over_z", 0.0),
        )

    @classmethod
    def from_dict(cls, params: dict[str, Any]) -> GcodeParameters:
        """Create from legacy parameter dict (handles old key names)."""
        # Handle the old 'filament diameter' key with space
        if "filament diameter" in params and "filament_diameter" not in params:
            params["filament_diameter"] = params.pop("filament diameter")
        return cls.__from_data__(params)
