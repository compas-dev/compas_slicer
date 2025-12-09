from __future__ import annotations

from typing import Any

__all__ = ['print_organization_default_param']

DEFAULT_PARAMETERS: dict[str, Any] = {}


def print_organization_default_param(key: str) -> Any:
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
    raise ValueError(f'Parameter key "{key}" not in print_organization defaults.')


# Backwards compatibility alias
default_parameters = DEFAULT_PARAMETERS
