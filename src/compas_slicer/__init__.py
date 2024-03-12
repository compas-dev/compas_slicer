"""
********************************************************************************
compas_slicer
********************************************************************************

.. currentmodule:: compas_slicer


.. toctree::
    :maxdepth: 1

    geometry
    slicers
    print_organization
    pre_processing
    post_processing
    utilities

"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import os
import compas


__author__ = ['Ioanna Mitropoulou and Joris Burger']
__copyright__ = 'Copyright 2020 ETH Zurich'
__license__ = 'MIT License'
__email__ = 'mitropoulou@arch.ethz.ch'
__version__ = '0.6.2'


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))

# Check if package is installed from git
# If that's the case, try to append the current head's hash to __version__
try:
    git_head_file = compas._os.absjoin(HOME, '.git', 'HEAD')

    if os.path.exists(git_head_file):
        # git head file contains one line that looks like this:
        # ref: refs/heads/master
        with open(git_head_file, 'r') as git_head:
            _, ref_path = git_head.read().strip().split(' ')
            ref_path = ref_path.split('/')

            git_head_refs_file = compas._os.absjoin(HOME, '.git', *ref_path)

        if os.path.exists(git_head_refs_file):
            with open(git_head_refs_file, 'r') as git_head_ref:
                git_commit = git_head_ref.read().strip()
                __version__ += '-' + git_commit[:8]
except Exception:
    pass

from .geometry import *  # noqa: F401 E402 F403
from .slicers import *  # noqa: F401 E402 F403
from .print_organization import *  # noqa: F401 E402 F403
from .utilities import *  # noqa: F401 E402 F403
from .post_processing import *  # noqa: F401 E402 F403
from .pre_processing import *  # noqa: F401 E402 F403
from .parameters import *  # noqa: F401 E402 F403

__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
