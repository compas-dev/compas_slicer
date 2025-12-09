"""
********************************************************************************
slicers
********************************************************************************

.. currentmodule:: compas_slicer.slicers


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    BaseSlicer


BaseSlicer
----------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    PlanarSlicer
    InterpolationSlicer
"""


from .base_slicer import *  # noqa: F401 F403
from .interpolation_slicer import *  # noqa: F401 E402 F403
from .planar_slicer import *  # noqa: F401 E402 F403
from .planar_slicing import *  # noqa: F401 E402 F403
from .scalar_field_slicer import *  # noqa: F401 E402 F403
from .uv_slicer import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]
