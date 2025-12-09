from __future__ import annotations

from typing import Any

__all__ = ['interpolation_slicing_default_param']

DEFAULT_PARAMETERS: dict[str, Any] = {
    # geodesics method
    'target_LOW_geodesics_method': 'heat_cgal',
    'target_HIGH_geodesics_method': 'heat_cgal',
    # union method for HIGH target
    # if all are false, then default 'min' method is used
    'target_HIGH_smooth_union': [False, [10.0]],  # blend radius
    'target_HIGH_chamfer_union': [False, [100.0]],  # size
    'target_HIGH_stairs_union': [False, [80.0, 3]],  # size, n-1 number of peaks
    'uneven_upper_targets_offset': 0,
}


def interpolation_slicing_default_param(key: str) -> Any:
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
    raise ValueError(f'Parameter key "{key}" not in interpolation_slicing defaults.')


# Backwards compatibility alias
default_parameters = DEFAULT_PARAMETERS
