import logging
from compas_slicer.parameters import get_param

logger = logging.getLogger('logger')

__all__ = ['create_gcode_text']


def create_gcode_text(printpoints_dict, parameters):
    """ Creates a gcode text file
    Parameters
    ----------
    printpoints_dict: dict with compas_slicer.geometry.Printpoint instances.
        The keys of the dictionary are setup in the following way:
        {['layer_%d' % i] =
            {['path_%d' % i] =
                [printpoint_1 , ....., printpoint_n ]
            }
        }
    parameters : dict with gcode parameters.
        The defaults for those parameters are in the file compas_slicer.parameters.defaults_gcode.

    Returns
    ----------
    str, gcode text file
    """
    NL = chr(10)
    logger.info('Generating gcode')
    gcode = ''

    ############################################
    # get all the necessary parameters:    
    # Physical parameters
    delta = get_param(parameters, key='delta', defaults_type='gcode') # boolean for delta printers
    nozzle_diameter = get_param(parameters, key='nozzle_diameter', defaults_type='gcode')  #in mm
    filament diameter = get_param(parameters, key='filament diameter', defaults_type='gcode')  #in mm
    
    # Dimensional parameters
    layer_width = get_param(parameters, key='layer_width', defaults_type='gcode')  #in mm
    
    # Temperature parameters
    extruder_temperature = get_param(parameters, key='extruder_temperature', defaults_type='gcode')  #in °C
    bed_temperature = get_param(parameters, key='bed_temperature', defaults_type='gcode')  #in °C
    fan_speed = get_param(parameters, key='bed_temperature', defaults_type='gcode')  #0-255
    fan_start_z = get_param(parameters, key='fan_start_z', defaults_type='gcode')  #in mm
    
    # Movement parameters
    feedrate = get_param(parameters, key='feedrate', defaults_type='gcode')  #in mm/s
    feedrate_travel = get_param(parameters, key='feedrate_travel', defaults_type='gcode')  #in mm/s
    feedrate_low = get_param(parameters, key='feedrate_low', defaults_type='gcode')  #in mm/s
    feedrate_retraction = get_param(parameters, key='feedrate_retraction', defaults_type='gcode')  #in mm/s   
    # acceleration = get_param(parameters, key='acceleration', defaults_type='gcode')  #in mm/s²   
    # jerk = get_param(parameters, key='jerk', defaults_type='gcode')  #in mm/s
    
    # Retraction
    z_hop = get_param(parameters, key='z_hop', defaults_type='gcode')  #in mm
    retraction_length = get_param(parameters, key='retraction_length', defaults_type='gcode')  #in mm
    retraction_min_travel = get_param(parameters, key='retraction_min_travel', defaults_type='gcode')  #in mm
    ############################################ / get parmeters
    
    ############################################ 
    # gcode header
    gcode = ''
    gcode += "Sliced with compas_slicer (Ioana Mitropolou mitropoulou@arch.ethz.ch @ioanna21; Joris Burger burger@arch.ethz.ch @joburger)" + NL
    gcode += "Gcode generated with compas_slicer Andrei Jipa <mitropoulou@arch.ethz.ch>)" + NL
    gcode += "T0                              ;set Tool" + NL # for printing with multiple nozzles this will become useful
    gcode += "G21                             ;metric values" + NL
    gcode += "G90                             ;absolute positioning" + NL
    gcode += "M107                            ;start With the fan Off" + NL
    gcode += "M140 S" + str(bed_temperature) + "                        ;Set Bed Temperature Fast" + NL
    gcode += "M104 S" + str(extruder_temperature) + "                       ;Set Extruder Temperature Fast" + NL
    gcode += "M109 S" + str(extruder_temperature) + "                       ;Set Extruder Temperature and Wait" + NL
    gcode += "M190 S" + str(bed_temperature) + "                        ;Set Bed Temperature + wait" + NL
    gcode += "G21                             ;metric values" + NL
    gcode += "G90                             ;absolute positioning" + NL
    gcode += "M83                             ;set E-values to relative while in absolute mode" + NL
    gcode += "G28 X0 Y0                       ;home X and Y axes" + NL
    gcode += "G28 Z0                          ;home Z axis independently" + NL
    gcode += "G1 F4500                        ;set feedrate to 4,500 mm/min (75 mm/s)" + NL
    gcode += "G1 Z15.0                        ;move nozzle up 15mm" + NL
    gcode += "G1 F140 E29                     ;extruded slowly some filament (default: 29mm)" + NL
    gcode += "G92 E0                          ;reset the extruded length to 0" + NL #this is redundant after M83, but should not be forgotten in case M83 is skipped
    gcode += "G1 F6000                        ;set feedrate to 6000 mm/min (100 mm/s)" + NL
    gcode += "M117 compas gcode print...      ;show up text on LCD" + NL
    ############################################  / header
    
    
    # Iterate through the printpoints_dict and add information to the gcode str
    for layer_key in printpoints_dict:
        for path_key in printpoints_dict[layer_key]:

            gcode += 'this is a command %.4f %.4f %.4f \n' % (z_hop, extruder_temp, bed_temp)  # just remove this line

            # .... gcode += 'command'

    return gcode
