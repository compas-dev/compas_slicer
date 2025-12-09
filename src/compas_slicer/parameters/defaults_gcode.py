from __future__ import annotations

from typing import Any

__all__ = ['gcode_default_param']

DEFAULT_PARAMETERS: dict[str, Any] = {
    # Physical parameters
    'nozzle_diameter': 0.4,  # mm
    'filament_diameter': 1.75,  # mm, for calculating E
    'filament diameter': 1.75,  # legacy key with space
    'delta': False,  # boolean for delta printers
    'print_volume_x': 300,  # mm
    'print_volume_y': 300,  # mm
    'print_volume_z': 600,  # mm
    # Dimensional parameters
    'layer_width': 0.6,  # mm
    # Temperature parameters
    'extruder_temperature': 200,  # °C
    'bed_temperature': 60,  # °C
    'fan_speed': 255,  # 0-255
    'fan_start_z': 0,  # mm; height at which fan starts
    # Movement parameters
    'flowrate': 1,  # fraction; global flow multiplier
    'feedrate': 3600,  # mm/min
    'feedrate_travel': 4800,  # mm/min
    'feedrate_low': 1800,  # mm/min
    'feedrate_retraction': 2400,  # mm/min
    'acceleration': 0,  # mm/s²; 0 = driver default
    'jerk': 0,  # mm/s; 0 = driver default
    # Retraction
    'z_hop': 0.5,  # mm
    'retraction_length': 1,  # mm
    'retraction_min_travel': 6,  # mm; below this, no retraction
    # Adhesion parameters
    'flow_over': 1,  # fraction; overextrusion for z < min_over_z
    'min_over_z': 0,  # mm; height below which overextrusion applies
}


def gcode_default_param(key: str) -> Any:
    """Return the default parameter with the specified key.

    Parameters
    ----------
    key : str
        Parameter key.

    Returns
    -------
    Any
        Default parameter value.

    Raises
    ------
    ValueError
        If key not found in defaults.

    """
    if key in DEFAULT_PARAMETERS:
        return DEFAULT_PARAMETERS[key]
    raise ValueError(f'Parameter key "{key}" not in gcode defaults.')


# Backwards compatibility alias
default_parameters = DEFAULT_PARAMETERS
