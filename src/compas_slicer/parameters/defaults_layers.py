from __future__ import annotations

from typing import Any

__all__ = ['layers_default_param']

DEFAULT_PARAMETERS: dict[str, Any] = {
    'avg_layer_height': 5.0,
    'min_layer_height': 0.5,
    'max_layer_height': 10.0,
    'vertical_layers_max_centroid_dist': 25.0,
}


def layers_default_param(key: str) -> Any:
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
    raise ValueError(f'Parameter key "{key}" not in layers defaults.')


# Backwards compatibility alias
default_parameters = DEFAULT_PARAMETERS
