"""
********************************************************************************
compas_slicer.functionality
********************************************************************************



positioning ideas todo
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

### Polyline simplification
from .simplify_paths_rdp import *  # noqa: F401 E402 F403

### Sorting
from .align_seams import *  # noqa: F401 E402 F403
from .smooth_seams import *  # noqa: F401 E402 F403
from .sort_per_segment import *  # noqa: F401 E402 F403
from .sort_per_shortest_path_mlrose import *  # noqa: F401 E402 F403

### Positioning
from .center_on_build_platform import *  # noqa: F401 E402 F403
from .move_mesh_to_point import *  # noqa: F401 E402 F403
from .get_mid_pt_base import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]
