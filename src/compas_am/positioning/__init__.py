"""
********************************************************************************
compas_am.position
********************************************************************************
    define working area/bounds 
    Maybe have some presets for mainstream machines like UR5
    position and orient input shape within reach
    orient shape to reduce need for support 
    Identify not fitting areas
    segmentation - design seams (this could be on its own module)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from .centering_on_build_platform import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]