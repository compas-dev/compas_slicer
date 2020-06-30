"""
********************************************************************************
compas_slicer.polyline_simplification
********************************************************************************
    Descrete polylines: 
        cull printpoints within a threshold (to reduce too many input curves)
        cull printpoints based on curvature - adaptive polygon simplification

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import compas

from .simplify_paths_curvature import *  # noqa: F401 E402 F403
if not compas.IPY:
    from .simplify_paths_rdp import *  # noqa: F401 E402 F403


__all__ = [name for name in dir() if not name.startswith('_')]