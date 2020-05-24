"""
********************************************************************************
compas_am.polyline_simplification
********************************************************************************
    Descrete polylines: 
        cull points within a threshold (to reduce too many input curves)
        cull points based on curvature - adaptive polygon simplification

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from .curvature_subsampling import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]