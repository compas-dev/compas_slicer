"""
********************************************************************************
compas_slicer.slicers
********************************************************************************

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
    CurvedSlicer
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .base_slicer import *  # noqa: F401 E402 F403
from .planar_slicer import *  # noqa: F401 E402 F403
from .curved_slicer import *  # noqa: F401 E402 F403
from .planar_slice_functions import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]
