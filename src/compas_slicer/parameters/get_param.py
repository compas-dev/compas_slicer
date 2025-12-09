from __future__ import annotations

from typing import Any, Literal

import compas_slicer

__all__ = ['get_param']

DefaultsType = Literal['interpolation_slicing', 'gcode', 'layers', 'print_organization']


def get_param(params: dict[str, Any], key: str, defaults_type: DefaultsType) -> Any:
    """Get parameter value from dict or fall back to defaults.

    Parameters
    ----------
    params : dict[str, Any]
        Parameters dictionary.
    key : str
        Parameter key to look up.
    defaults_type : DefaultsType
        Which defaults to use: 'interpolation_slicing', 'gcode', 'layers', or 'print_organization'.

    Returns
    -------
    Any
        params[key] if key in params, otherwise the default value.

    Raises
    ------
    ValueError
        If defaults_type is not recognized.

    """
    if key in params:
        return params[key]

    if defaults_type == 'interpolation_slicing':
        return compas_slicer.parameters.interpolation_slicing_default_param(key)
    elif defaults_type == 'gcode':
        return compas_slicer.parameters.gcode_default_param(key)
    elif defaults_type == 'layers':
        return compas_slicer.parameters.layers_default_param(key)
    elif defaults_type == 'print_organization':
        return compas_slicer.parameters.gcode_default_param(key)
    else:
        raise ValueError(f'The specified parameter type: {defaults_type} does not exist.')
