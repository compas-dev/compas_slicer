import logging
import math
from compas_slicer.parameters import get_param
from compas.geometry import Point, Vector
from compas_slicer.geometry import PrintPoint

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

    #######################################################################
    # get all the necessary parameters:    
    # Physical parameters
    delta = get_param(parameters, key='delta', defaults_type='gcode')  # boolean for delta printers
    nozzle_diameter = get_param(parameters, key='nozzle_diameter', defaults_type='gcode')  # in mm
    filament_diameter = get_param(parameters, key='filament diameter', defaults_type='gcode')  # in mm

    # Dimensional parameters
    path_width = get_param(parameters, key='layer_width', defaults_type='gcode')  # in mm

    # Temperature parameters
    extruder_temperature = get_param(parameters, key='extruder_temperature', defaults_type='gcode')  # in °C
    bed_temperature = get_param(parameters, key='bed_temperature', defaults_type='gcode')  # in °C
    fan_speed = get_param(parameters, key='bed_temperature', defaults_type='gcode')  # 0-255
    fan_start_z = get_param(parameters, key='fan_start_z', defaults_type='gcode')  # in mm

    # Movement parameters
    feedrate = get_param(parameters, key='feedrate', defaults_type='gcode')  # in mm/s
    feedrate_travel = get_param(parameters, key='feedrate_travel', defaults_type='gcode')  # in mm/s
    feedrate_low = get_param(parameters, key='feedrate_low', defaults_type='gcode')  # in mm/s
    feedrate_retraction = get_param(parameters, key='feedrate_retraction', defaults_type='gcode')  # in mm/s
    # acceleration = get_param(parameters, key='acceleration', defaults_type='gcode')  #in mm/s²   
    # jerk = get_param(parameters, key='jerk', defaults_type='gcode')  #in mm/s

    # Retraction and hop parameters
    z_hop = get_param(parameters, key='z_hop', defaults_type='gcode')  # in mm
    retraction_length = get_param(parameters, key='retraction_length', defaults_type='gcode')  # in mm
    retraction_min_travel = get_param(parameters, key='retraction_min_travel', defaults_type='gcode')  # in mm

    # Adhesion parameters
    flow_over = get_param(parameters, key='flow_over', defaults_type='gcode')  # !!!!!!!!!!NOT SET YET!!!
    min_over_z = get_param(parameters, key='min_over_z', defaults_type='gcode')  # !!!!!!!!!!NOT SET YET!!!
    # ______________________________________________________________________/ get parmeters

    #######################################################################  
    # gcode header
    gcode += "Sliced with compas_slicer (Ioana Mitropolou mitropoulou@arch.ethz.ch @ioanna21; Joris Burger burger@arch.ethz.ch @joburger)" + NL
    gcode += "Gcode generated with compas_slicer Andrei Jipa <mitropoulou@arch.ethz.ch>)" + NL
    gcode += "T0                              ;set Tool" + NL  # for printing with multiple nozzles this will become useful
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
    gcode += "G92 E0                          ;reset the extruded length to 0" + NL  # this is redundant after M83, but should not be forgotten in case M83 is skipped
    gcode += "G1 F6000                        ;set feedrate to 6000 mm/min (100 mm/s)" + NL
    gcode += "G1 F" + str(feedrate_low) + "                              ;set initial Feedrate" + NL
    gcode += "M117 compas gcode print...      ;show up text on LCD" + NL
    # ______________________________________________________________________/ header

    #######################################################################  
    # global parameters        
    retraction_on = True  # boolean; is true when retraction is toggled
    fan_on = False  # boolean; is true when fan is toggled
    prev_point = PrintPoint(Point(0, 0, 0), layer_height=1.0,
                            mesh_normal=Vector(1.0, 0.0, 0.0))  # dummy print_point that is overwritten
    layer_height = 1.0  # dummy value that is overwritten
    # ______________________________________________________________________/ global parameters

    #######################################################################  
    # iterate all layers, paths
    print('')
    for i, layer_v in enumerate(printpoints_dict):
        for j, path_v in enumerate(printpoints_dict[layer_v]):
            for k, point_v in enumerate(printpoints_dict[layer_v][path_v]):
                layer_height = point_v.layer_height

                # Calculate relative length
                reL = ((point_v.pt.x - prev_point.pt.x) ** 2 + (point_v.pt.y - prev_point.pt.y) ** 2 + (
                        point_v.pt.z - prev_point.pt.z) ** 2) ** 0.5
                if k == 0:  # 'First point
                    # retract before moving to first point in path if necessary
                    if retraction_min_travel < reL:
                        gcode += "G1 F" + str(feedrate_retraction) + "    ;set ret sp" + NL
                        gcode += "G1" + " E-" + str(retraction_length) + "    ;ret fil" + NL
                        # ZHOP
                        gcode += "G1" + " Z" + '{:.3f}'.format(prev_point.pt.z + z_hop) + "    ;ZHop" + NL
                        gcode += "G1" + " F" + str(feedrate_travel) + "    ;set trav spd" + NL
                        retraction_on = True
                    else:
                        retraction_on = False
                    if retraction_on:  # TODO: combine this if clause in the min_Travel<reL above
                        gcode += "G1 X" + '{:.3f}'.format(point_v.pt.x) + " Y" + '{:.3f}'.format(point_v.pt.y) + NL
                        # reverse hop and retract after reaching the first point
                        gcode += "G1 F" + str(feedrate_retraction) + "          ;set ret spd" + NL
                        gcode += "G1" + " Z" + '{:.3f}'.format(point_v.pt.z) + "    ;Rev ZHop" + NL
                        gcode += "G1" + " E" + str(retraction_length) + "    ;rev fil ret" + NL
                        gcode += "G1" + " F" + str(feedrate) + "    ;set extr spd" + NL
                    else:
                        if point_v.z != prev_point.z:
                            gcode += "G1" + " Z" + '{:.3f}'.format(point_v.pt.z) + "    ;Move in Z" + NL
                        gcode += "G1 X" + '{:.3f}'.format(point_v.pt.x) + " Y" + '{:.3f}'.format(point_v.pt.y) + NL
                else:  # from 2nd poin onwards
                    # tmpflow = myflow.Branch(b)(i) here we can set the flow multiplier
                    # Calculate feedrate
                    E_val = 4 * reL * layer_height * path_width / (math.pi * (filament_diameter ** 2))
                    if point_v.pt.z < min_over_z:  # TODO: REPLACE WITH REPEAT... UNTIL for NXT VErison
                        E_val *= flow_over
                    gcode += "G1 X" + '{:.3f}'.format(point_v.pt.x) + " Y" + '{:.3f}'.format(
                        point_v.pt.y) + " E" + '{:.3f}'.format(E_val) + NL
                prev_point = point_v
        if fan_on == False:
            if i * layer_height >= fan_start_z:  # 'Fan On:
                gcode += "M106 S" + str(fan_speed) + "    ;set fan on to set speed" + NL

                # 'retract after last branch/contour
    gcode += "G1 F" + str(feedrate_retraction) + "    ;set ret spd" + NL
    gcode += "G1" + " E-" + str(retraction_length) + "    ;ret fil" + NL
    gcode += "G1" + " Z" + '{:.3f}'.format(3 * (prev_point.pt.z + z_hop)) + "    ;ZHop" + NL
    gcode += "G1 F" + str(feedrate_travel) + "    ;set ret spd" + NL
    retraction_on = True

    #######################################################################
    # Footer
    gcode += "M106 S0                     ;set fan on to 200/255 speed" + NL
    gcode += "M201 X500 Y500              ;Set acceleration To 500mm/s^2" + NL
    gcode += "G1" + " F 1000              ;set travel speed to 1000 mm/min" + NL
    gcode += "G1 X0 Y0                    ;Home X and Y" + NL
    gcode += "M104 S0                     ;extruder heater Off" + NL
    gcode += "M140 S0                     ;heated bed heater Off (If it exists)" + NL
    gcode += "M84                         ;steppers off" + NL
    # ______________________________________________________________________/ footer

    return gcode
