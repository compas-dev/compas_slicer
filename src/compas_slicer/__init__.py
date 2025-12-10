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

from pathlib import Path

__author__ = ["Ioanna Mitropoulou", "Joris Burger"]
__copyright__ = "Copyright 2020 ETH Zurich"
__license__ = "MIT License"
__email__ = "mitropoulou@arch.ethz.ch"
__version__ = "0.8.0"


HERE = Path(__file__).parent
HOME = HERE.parent.parent
DATA = HOME / "data"
DOCS = HOME / "docs"
TEMP = HOME / "temp"

# Check if package is installed from git
# If that's the case, try to append the current head's hash to __version__
try:
    git_head_file = HOME / ".git" / "HEAD"

    if git_head_file.exists():
        # git head file contains one line that looks like this:
        # ref: refs/heads/master
        ref_path = git_head_file.read_text().strip().split(" ")[1].split("/")
        git_head_refs_file = HOME / ".git" / Path(*ref_path)

        if git_head_refs_file.exists():
            git_commit = git_head_refs_file.read_text().strip()
            __version__ += "-" + git_commit[:8]
except Exception:
    # Git version detection is optional, fail silently if not in git repo
    pass

from .config import *  # noqa: F401 E402 F403
from .geometry import *  # noqa: F401 E402 F403
from .parameters import *  # noqa: F401 E402 F403
from .post_processing import *  # noqa: F401 E402 F403
from .pre_processing import *  # noqa: F401 E402 F403
from .print_organization import *  # noqa: F401 E402 F403
from .slicers import *  # noqa: F401 E402 F403
from .utilities import *  # noqa: F401 E402 F403

__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
