"""
********************************************************************************
compas_slicer.utilities
********************************************************************************

Functions
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    terminal_command
    utils_numpy
    utils

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import compas

from .utils import *  # noqa: F401 E402 F403
from .terminal_command import *  # noqa: F401 E402 F403

if not compas.IPY:
    from .utils_numpy import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]
