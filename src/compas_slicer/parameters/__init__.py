"""
********************************************************************************
parameters
********************************************************************************

.. autosummary::
    :toctree: generated/
    :nosignatures:

    get_param
    defaults_curved_slicing
    defaults_gcode
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#  Polyline simplification
from .get_param import *  # noqa: F401 E402 F403
from .defaults_interpolation_slicing import *  # noqa: F401 E402 F403
from .defaults_gcode import *  # noqa: F401 E402 F403
from .defaults_layers import *  # noqa: F401 E402 F403
from .defaults_print_organization import *  # noqa: F401 E402 F403


__all__ = [name for name in dir() if not name.startswith('_')]
