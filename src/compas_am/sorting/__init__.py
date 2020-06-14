"""
********************************************************************************
compas_am
********************************************************************************
    
    sort per layer - shortest path at the same z height
    sort per segment - less interruptions 
    sort by longest path
    
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import compas

from .seams import *  # noqa: F401 E402 F403
from .sort_per_segment import *  # noqa: F401 E402 F403

if not compas.IPY:
    from .sort_shortest_path_mlrose import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]