"""Configuration dataclasses for compas_slicer.

This module provides typed configuration objects with defaults loaded from
a TOML file. All configs are dataclasses with full type hints.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from compas.data import Data

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

__all__ = [
    "SlicerConfig",
    "InterpolationConfig",
    "GcodeConfig",
    "PrintConfig",
    "OutputConfig",
    "GeodesicsMethod",
    "UnionMethod",
    "load_defaults",
]

# Load defaults from TOML at module import time
_DEFAULTS_PATH = Path(__file__).parent / "data" / "defaults.toml"


def load_defaults() -> dict[str, Any]:
    """Load default configuration from TOML file.

    Returns
    -------
    dict[str, Any]
        Dictionary with sections: slicer, interpolation, gcode

    """
    with open(_DEFAULTS_PATH, "rb") as f:
        return tomllib.load(f)


_DEFAULTS = load_defaults()


class GeodesicsMethod(str, Enum):
    """Method for computing geodesic distances."""

    EXACT_IGL = "exact_igl"
    HEAT_IGL = "heat_igl"
    HEAT_CGAL = "heat_cgal"
    HEAT = "heat"


class UnionMethod(str, Enum):
    """Method for combining target boundaries."""

    MIN = "min"
    SMOOTH = "smooth"
    CHAMFER = "chamfer"
    STAIRS = "stairs"


@dataclass
class OutputConfig:
    """Configuration for output paths.

    Attributes
    ----------
    base_path : Path
        Base directory for input/output.
    output_subdir : str
        Name of the output subdirectory (created if not exists).

    """

    base_path: Path = field(default_factory=Path.cwd)
    output_subdir: str = "output"

    @property
    def output_path(self) -> Path:
        """Get the full output path, creating directory if needed."""
        out = self.base_path / self.output_subdir
        out.mkdir(exist_ok=True)
        return out

    def __post_init__(self) -> None:
        if isinstance(self.base_path, str):
            self.base_path = Path(self.base_path)


def _slicer_defaults() -> dict[str, Any]:
    return _DEFAULTS.get("slicer", {})


def _interpolation_defaults() -> dict[str, Any]:
    return _DEFAULTS.get("interpolation", {})


def _gcode_defaults() -> dict[str, Any]:
    return _DEFAULTS.get("gcode", {})


@dataclass
class SlicerConfig(Data):
    """Configuration for slicer operations.

    Attributes
    ----------
    layer_height : float
        Height between layers in mm.
    min_path_length : int
        Minimum number of points for a valid path.
    close_path_tolerance : float
        Distance threshold for considering path endpoints as coincident.

    """

    layer_height: float = field(default_factory=lambda: _slicer_defaults().get("layer_height", 2.0))
    min_path_length: int = field(default_factory=lambda: _slicer_defaults().get("min_path_length", 2))
    close_path_tolerance: float = field(default_factory=lambda: _slicer_defaults().get("close_path_tolerance", 0.00001))

    def __post_init__(self) -> None:
        super().__init__()

    @property
    def __data__(self) -> dict[str, Any]:
        return {
            "layer_height": self.layer_height,
            "min_path_length": self.min_path_length,
            "close_path_tolerance": self.close_path_tolerance,
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> SlicerConfig:
        d = _slicer_defaults()
        return cls(
            layer_height=data.get("layer_height", d.get("layer_height", 2.0)),
            min_path_length=data.get("min_path_length", d.get("min_path_length", 2)),
            close_path_tolerance=data.get("close_path_tolerance", d.get("close_path_tolerance", 0.00001)),
        )


@dataclass
class InterpolationConfig(Data):
    """Configuration for interpolation (curved) slicing.

    Attributes
    ----------
    avg_layer_height : float
        Average height between layers.
    min_layer_height : float
        Minimum layer height.
    max_layer_height : float
        Maximum layer height.
    vertical_layers_max_centroid_dist : float
        Maximum distance for grouping paths into vertical layers.
    target_low_geodesics_method : GeodesicsMethod
        Method for computing geodesics to low boundary.
    target_high_geodesics_method : GeodesicsMethod
        Method for computing geodesics to high boundary.
    target_high_union_method : UnionMethod
        Method for combining high target boundaries.
    target_high_union_params : list[float]
        Parameters for the union method.
    uneven_upper_targets_offset : float
        Offset for uneven upper targets.

    """

    avg_layer_height: float = field(default_factory=lambda: _interpolation_defaults().get("avg_layer_height", 5.0))
    min_layer_height: float = field(default_factory=lambda: _interpolation_defaults().get("min_layer_height", 0.5))
    max_layer_height: float = field(default_factory=lambda: _interpolation_defaults().get("max_layer_height", 10.0))
    vertical_layers_max_centroid_dist: float = field(
        default_factory=lambda: _interpolation_defaults().get("vertical_layers_max_centroid_dist", 25.0)
    )
    target_low_geodesics_method: GeodesicsMethod = field(
        default_factory=lambda: GeodesicsMethod(_interpolation_defaults().get("target_low_geodesics_method", "heat_igl"))
    )
    target_high_geodesics_method: GeodesicsMethod = field(
        default_factory=lambda: GeodesicsMethod(_interpolation_defaults().get("target_high_geodesics_method", "heat_igl"))
    )
    target_high_union_method: UnionMethod = field(
        default_factory=lambda: UnionMethod(_interpolation_defaults().get("target_high_union_method", "min"))
    )
    target_high_union_params: list[float] = field(
        default_factory=lambda: list(_interpolation_defaults().get("target_high_union_params", []))
    )
    uneven_upper_targets_offset: float = field(
        default_factory=lambda: _interpolation_defaults().get("uneven_upper_targets_offset", 0.0)
    )

    def __post_init__(self) -> None:
        super().__init__()
        # Convert string enums if needed
        if isinstance(self.target_low_geodesics_method, str):
            self.target_low_geodesics_method = GeodesicsMethod(self.target_low_geodesics_method)
        if isinstance(self.target_high_geodesics_method, str):
            self.target_high_geodesics_method = GeodesicsMethod(self.target_high_geodesics_method)
        if isinstance(self.target_high_union_method, str):
            self.target_high_union_method = UnionMethod(self.target_high_union_method)

    @property
    def __data__(self) -> dict[str, Any]:
        return {
            "avg_layer_height": self.avg_layer_height,
            "min_layer_height": self.min_layer_height,
            "max_layer_height": self.max_layer_height,
            "vertical_layers_max_centroid_dist": self.vertical_layers_max_centroid_dist,
            "target_low_geodesics_method": self.target_low_geodesics_method.value,
            "target_high_geodesics_method": self.target_high_geodesics_method.value,
            "target_high_union_method": self.target_high_union_method.value,
            "target_high_union_params": self.target_high_union_params,
            "uneven_upper_targets_offset": self.uneven_upper_targets_offset,
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> InterpolationConfig:
        d = _interpolation_defaults()
        return cls(
            avg_layer_height=data.get("avg_layer_height", d.get("avg_layer_height", 5.0)),
            min_layer_height=data.get("min_layer_height", d.get("min_layer_height", 0.5)),
            max_layer_height=data.get("max_layer_height", d.get("max_layer_height", 10.0)),
            vertical_layers_max_centroid_dist=data.get(
                "vertical_layers_max_centroid_dist", d.get("vertical_layers_max_centroid_dist", 25.0)
            ),
            target_low_geodesics_method=data.get(
                "target_low_geodesics_method", d.get("target_low_geodesics_method", "heat_igl")
            ),
            target_high_geodesics_method=data.get(
                "target_high_geodesics_method", d.get("target_high_geodesics_method", "heat_igl")
            ),
            target_high_union_method=data.get("target_high_union_method", d.get("target_high_union_method", "min")),
            target_high_union_params=data.get("target_high_union_params", d.get("target_high_union_params", [])),
            uneven_upper_targets_offset=data.get(
                "uneven_upper_targets_offset", d.get("uneven_upper_targets_offset", 0.0)
            ),
        )


@dataclass
class GcodeConfig(Data):
    """Configuration for G-code generation.

    Attributes
    ----------
    nozzle_diameter : float
        Nozzle diameter in mm.
    filament_diameter : float
        Filament diameter in mm.
    delta : bool
        True for delta printers.
    print_volume : tuple[float, float, float]
        Print volume (x, y, z) in mm.
    layer_width : float
        Layer width in mm.
    extruder_temperature : int
        Extruder temperature in C.
    bed_temperature : int
        Bed temperature in C.
    fan_speed : int
        Fan speed (0-255).
    fan_start_z : float
        Height at which fan starts in mm.
    flowrate : float
        Global flow multiplier.
    feedrate : float
        Print feedrate in mm/min.
    feedrate_travel : float
        Travel feedrate in mm/min.
    feedrate_low : float
        Low feedrate in mm/min.
    feedrate_retraction : float
        Retraction feedrate in mm/min.
    acceleration : float
        Acceleration in mm/s2. 0 = driver default.
    jerk : float
        Jerk in mm/s. 0 = driver default.
    z_hop : float
        Z hop distance in mm.
    retraction_length : float
        Retraction length in mm.
    retraction_min_travel : float
        Minimum travel distance for retraction in mm.
    flow_over : float
        Overextrusion factor below min_over_z.
    min_over_z : float
        Height below which overextrusion applies.

    """

    nozzle_diameter: float = field(default_factory=lambda: _gcode_defaults().get("nozzle_diameter", 0.4))
    filament_diameter: float = field(default_factory=lambda: _gcode_defaults().get("filament_diameter", 1.75))
    delta: bool = field(default_factory=lambda: _gcode_defaults().get("delta", False))
    print_volume: tuple[float, float, float] = field(
        default_factory=lambda: tuple(_gcode_defaults().get("print_volume", [300.0, 300.0, 600.0]))
    )
    layer_width: float = field(default_factory=lambda: _gcode_defaults().get("layer_width", 0.6))
    extruder_temperature: int = field(default_factory=lambda: _gcode_defaults().get("extruder_temperature", 200))
    bed_temperature: int = field(default_factory=lambda: _gcode_defaults().get("bed_temperature", 60))
    fan_speed: int = field(default_factory=lambda: _gcode_defaults().get("fan_speed", 255))
    fan_start_z: float = field(default_factory=lambda: _gcode_defaults().get("fan_start_z", 0.0))
    flowrate: float = field(default_factory=lambda: _gcode_defaults().get("flowrate", 1.0))
    feedrate: float = field(default_factory=lambda: _gcode_defaults().get("feedrate", 3600.0))
    feedrate_travel: float = field(default_factory=lambda: _gcode_defaults().get("feedrate_travel", 4800.0))
    feedrate_low: float = field(default_factory=lambda: _gcode_defaults().get("feedrate_low", 1800.0))
    feedrate_retraction: float = field(default_factory=lambda: _gcode_defaults().get("feedrate_retraction", 2400.0))
    acceleration: float = field(default_factory=lambda: _gcode_defaults().get("acceleration", 0.0))
    jerk: float = field(default_factory=lambda: _gcode_defaults().get("jerk", 0.0))
    z_hop: float = field(default_factory=lambda: _gcode_defaults().get("z_hop", 0.5))
    retraction_length: float = field(default_factory=lambda: _gcode_defaults().get("retraction_length", 1.0))
    retraction_min_travel: float = field(default_factory=lambda: _gcode_defaults().get("retraction_min_travel", 6.0))
    flow_over: float = field(default_factory=lambda: _gcode_defaults().get("flow_over", 1.0))
    min_over_z: float = field(default_factory=lambda: _gcode_defaults().get("min_over_z", 0.0))

    def __post_init__(self) -> None:
        super().__init__()
        # Ensure print_volume is a tuple
        if isinstance(self.print_volume, list):
            self.print_volume = tuple(self.print_volume)

    @property
    def print_volume_x(self) -> float:
        return self.print_volume[0]

    @property
    def print_volume_y(self) -> float:
        return self.print_volume[1]

    @property
    def print_volume_z(self) -> float:
        return self.print_volume[2]

    @property
    def __data__(self) -> dict[str, Any]:
        return {
            "nozzle_diameter": self.nozzle_diameter,
            "filament_diameter": self.filament_diameter,
            "delta": self.delta,
            "print_volume": list(self.print_volume),
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
    def __from_data__(cls, data: dict[str, Any]) -> GcodeConfig:
        d = _gcode_defaults()
        # Handle both tuple and separate x/y/z keys for print_volume
        if "print_volume" in data:
            print_volume = tuple(data["print_volume"])
        else:
            default_vol = d.get("print_volume", [300.0, 300.0, 600.0])
            print_volume = (
                data.get("print_volume_x", default_vol[0]),
                data.get("print_volume_y", default_vol[1]),
                data.get("print_volume_z", default_vol[2]),
            )

        return cls(
            nozzle_diameter=data.get("nozzle_diameter", d.get("nozzle_diameter", 0.4)),
            filament_diameter=data.get("filament_diameter", d.get("filament_diameter", 1.75)),
            delta=data.get("delta", d.get("delta", False)),
            print_volume=print_volume,
            layer_width=data.get("layer_width", d.get("layer_width", 0.6)),
            extruder_temperature=data.get("extruder_temperature", d.get("extruder_temperature", 200)),
            bed_temperature=data.get("bed_temperature", d.get("bed_temperature", 60)),
            fan_speed=data.get("fan_speed", d.get("fan_speed", 255)),
            fan_start_z=data.get("fan_start_z", d.get("fan_start_z", 0.0)),
            flowrate=data.get("flowrate", d.get("flowrate", 1.0)),
            feedrate=data.get("feedrate", d.get("feedrate", 3600.0)),
            feedrate_travel=data.get("feedrate_travel", d.get("feedrate_travel", 4800.0)),
            feedrate_low=data.get("feedrate_low", d.get("feedrate_low", 1800.0)),
            feedrate_retraction=data.get("feedrate_retraction", d.get("feedrate_retraction", 2400.0)),
            acceleration=data.get("acceleration", d.get("acceleration", 0.0)),
            jerk=data.get("jerk", d.get("jerk", 0.0)),
            z_hop=data.get("z_hop", d.get("z_hop", 0.5)),
            retraction_length=data.get("retraction_length", d.get("retraction_length", 1.0)),
            retraction_min_travel=data.get("retraction_min_travel", d.get("retraction_min_travel", 6.0)),
            flow_over=data.get("flow_over", d.get("flow_over", 1.0)),
            min_over_z=data.get("min_over_z", d.get("min_over_z", 0.0)),
        )


@dataclass
class PrintConfig(Data):
    """Unified configuration for print operations.

    This combines slicer, interpolation, and gcode configs into a single
    configuration object for convenience.

    Attributes
    ----------
    slicer : SlicerConfig
        Slicer configuration.
    interpolation : InterpolationConfig
        Interpolation slicing configuration.
    gcode : GcodeConfig
        G-code generation configuration.
    output : OutputConfig
        Output path configuration.

    """

    slicer: SlicerConfig = field(default_factory=SlicerConfig)
    interpolation: InterpolationConfig = field(default_factory=InterpolationConfig)
    gcode: GcodeConfig = field(default_factory=GcodeConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def __post_init__(self) -> None:
        super().__init__()

    @property
    def __data__(self) -> dict[str, Any]:
        return {
            "slicer": self.slicer.__data__,
            "interpolation": self.interpolation.__data__,
            "gcode": self.gcode.__data__,
            "output": {
                "base_path": str(self.output.base_path),
                "output_subdir": self.output.output_subdir,
            },
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> PrintConfig:
        output_data = data.get("output", {})
        return cls(
            slicer=SlicerConfig.__from_data__(data.get("slicer", {})),
            interpolation=InterpolationConfig.__from_data__(data.get("interpolation", {})),
            gcode=GcodeConfig.__from_data__(data.get("gcode", {})),
            output=OutputConfig(
                base_path=Path(output_data.get("base_path", ".")),
                output_subdir=output_data.get("output_subdir", "output"),
            ),
        )

    @classmethod
    def from_toml(cls, path: str | Path) -> PrintConfig:
        """Load configuration from a TOML file.

        Parameters
        ----------
        path : str | Path
            Path to TOML configuration file.

        Returns
        -------
        PrintConfig
            Configuration loaded from file.

        """
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls.__from_data__(data)
