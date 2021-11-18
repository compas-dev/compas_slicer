"""
********************************************************************************
print_organization
********************************************************************************

.. currentmodule:: compas_slicer.print_organization


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    BasePrintOrganizer


BasePrintOrganizer
------------------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    InterpolationPrintOrganizer


Functions
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    set_extruder_toggle
    override_extruder_toggle
    set_blend_radius
    add_safety_printpoints
    set_wait_time_on_sharp_corners
    set_wait_time_based_on_extruder_toggle
    override_wait_time
    set_linear_velocity_constant
    set_linear_velocity_per_layer
    set_linear_velocity_by_range
    set_linear_velocity_by_overhang

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from .base_print_organizer import *  # noqa: F401 E402 F403
from .planar_print_organizer import *  # noqa: F401 E402 F403
from .interpolation_print_organizer import *  # noqa: F401 E402 F403
from .scalar_field_print_organizer import *  # noqa: F401 E402 F403

from .curved_print_organization import *  # noqa: F401 E402 F403
from .print_organization_utilities import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]
