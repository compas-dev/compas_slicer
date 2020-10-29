"""
********************************************************************************
geometry
********************************************************************************

.. currentmodule:: compas_slicer.geometry


Geometry in compas_slicer consists out of a Layer, Path, or Printpoint.
A Layer is generated when a geometry is sliced into layers and can therefore be
seen as a 'slice' of a geometry. Layers are typically organized horizontally,
but can also be organized vertically. A Layer consists out of one, or multiple
Paths (depending on the geometry).
A Path is a contour within a layer. A Path consists out of a list of
compas.Points, plus some additional attributes.
A PrintPoint consists out of a single compas.geometry.Point, with additional
functionality added for the printing process.


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Layer
    Path
    PrintPoint
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .path import *  # noqa: F401 E402 F403
from .layer import *  # noqa: F401 E402 F403
from .print_point import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]
