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
    sort_per_segment

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
from .simplify_paths_rdp import *  # noqa: F401 E402 F403

#  Sorting
from .seams_align import *  # noqa: F401 E402 F403
from .seams_smooth import *  # noqa: F401 E402 F403
from .sort_paths_per_vertical_segment import *  # noqa: F401 E402 F403

#  Orienting
from .unify_paths_orientation import *  # noqa: F401 E402 F403

#  Additional
from .generate_brim import *  # noqa: F401 E402 F403
from .spiralize_contours import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]
