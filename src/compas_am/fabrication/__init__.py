"""
********************************************************************************
compas_am.commands
********************************************************************************

Thought 06.05.2020: Could it make sense to change 'fabrication' to 'output' to resonate better with 'input'?

-gcode

compas_am.commands

    generate commands
    save commands : save to Json, save to Gcode
    import commands
    
    Need to agree on a universal template for commands 
    Ex:
    Command
    (Frame: ... , End effector parameters: ..., Waiting time: ..., Robot configuration: ..., Blend radius: ..., 
    velocity: ..., acceleration: ... )

    Then each project can only fill in the parameters they need 


--------------------------------
compas_am.fabrication_data
    generate_ur_script(commands) 
    save_ur_script(script, filename)

    generate_rapid(commands) 
    save_rapid

compas_am.send_commands
    UR direct communication
    Rapid ?... 


"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from .command import *  # noqa: F401 E402 F403
from .gcode import *  # noqa: F401 E402 F403
from .machine_model import *  # noqa: F401 E402 F403
from .print_organizer import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]
