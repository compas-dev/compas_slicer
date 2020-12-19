"""
********************************************************************************
post_processing
********************************************************************************

Polyline simplification
=======================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    simplify_paths_rdp

Sorting
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    seams_align
    seams_smooth
    sort_per_vertical_segment

Additional
==========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    generate_brim
    spiralize_contours

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#  Polyline simplification
from .get_param import *  # noqa: F401 E402 F403
from .defaults_curved_slicing import *  # noqa: F401 E402 F403
from .defaults_gcode import *  # noqa: F401 E402 F403


__all__ = [name for name in dir() if not name.startswith('_')]