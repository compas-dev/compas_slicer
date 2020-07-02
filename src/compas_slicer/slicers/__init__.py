"""
********************************************************************************
compas_slicer.slicing
********************************************************************************
    Supports
        identify and visualize big overhangs 
        generate supports where needed

    Slicing
        slice planar layers with regular height
        slice planar layers with adaptive height
        slice curved layers 

    Infill
        infill generation

    align seams
    randomize seams
    orient curves 
    cull small curves 
    solve self intersections 
    other: find issues - Satinize the curves
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import compas

from .base_slicer import *  # noqa: F401 E402 F403
from .planar_slicer import *
if not compas.IPY:
    from .curved_slicer import *

if not compas.IPY:
    from compas_slicer.slicers.planar_slice_functions.planar_slicing_meshcut import *  # noqa: F401 E402 F403
    from compas_slicer.slicers.planar_slice_functions.planar_slicing_numpy import *  # noqa: F401 E402 F403
    from compas_slicer.slicers.planar_slice_functions.planar_slicing_cgal import *  # noqa: F401 E402 F403
    from compas_slicer.slicers.planar_slice_functions.planar_slicing_cgal_copy import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]
