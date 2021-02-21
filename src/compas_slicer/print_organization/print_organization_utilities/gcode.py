import logging
import math
from compas_slicer.parameters import get_param
from compas.geometry import Point, Vector, distance_point_point
from compas_slicer.geometry import PrintPoint
from datetime import datetime

logger = logging.getLogger('logger')

__all__ = ['create_gcode_text']


def create_gcode_text(print_organizer, parameters):
    """ Creates a gcode text file
    Parameters
    ----------
    print_organizer: :class: compas_slicer.print_organization.PrintOrganizer
    parameters : dict with gcode parameters.
        The defaults for those parameters are in the file compas_slicer.parameters.defaults_gcode.

    Returns
    ----------
    str, gcode text file
    """
    n_l = chr(10)  # new line
    # get time stamp
    now = datetime.now()
    datetimestamp = now.strftime("%H:%M:%S - %d %B %Y")
    logger.info('Generating gcode')
    gcode = ''

    #######################################################################
    # get all the necessary parameters:
    # Physical parameters
    # nozzle_diameter = get_param(parameters, key='nozzle_diameter', defaults_type='gcode')  # in mm
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
    feedrate_low = get_param(parameters, key='feedrate_low', defaults_type='gcode')  # in mm/s, for z < min_over_z
    feedrate_retraction = get_param(parameters, key='feedrate_retraction', defaults_type='gcode')  # in mm/s
    acceleration = get_param(parameters, key='acceleration', defaults_type='gcode')  # in mm/s²; ignored if 0
    jerk = get_param(parameters, key='jerk', defaults_type='gcode')  # in mm/s; if 0, the default driver value is used

    # Retraction and hop parameters
    z_hop = get_param(parameters, key='z_hop', defaults_type='gcode')  # in mm
    retraction_length = get_param(parameters, key='retraction_length', defaults_type='gcode')  # in mm
    retraction_min_travel = get_param(parameters, key='retraction_min_travel', defaults_type='gcode')  # in mm

    # Adhesion parameters
    flow_over = get_param(parameters, key='flow_over', defaults_type='gcode')  # as fraction > 1
    min_over_z = get_param(parameters, key='min_over_z', defaults_type='gcode')  # in mm
    # ______________________________________________________________________/ get parmeters

    # ######################################################################
    # gcode header
    gcode += ";Gcode with compas_slicer " + n_l
    gcode += ";Ioana Mitropolou <mitropoulou@arch.ethz.ch> @ioanna21" + n_l
    gcode += ";Joris Burger     <burger@arch.ethz.ch>      @joburger" + n_l
    gcode += ";Andrei Jipa      <jipa@arch.ethz.ch         @stratocaster>" + n_l
    gcode += ";MIT License" + n_l
    gcode += ";" + n_l
    gcode += ";generated " + datetimestamp + n_l
    gcode += ";" + n_l
    gcode += "T0                              ;set tool" + n_l  # for printing with multiple nozzles this will be useful
    gcode += "G21                             ;metric values" + n_l
    gcode += "G90                             ;absolute positioning" + n_l
    gcode += "M107                            ;start with the fan off" + n_l
    gcode += "M140 S%d                        ;set bed temperature fast" % bed_temperature + n_l
    gcode += "M104 S%d                        ;set extruder temperature fast" % extruder_temperature + n_l
    gcode += "M109 S%d                        ;set extruder temperature and wait" % extruder_temperature + n_l
    gcode += "M190 S%d                        ;set bed temperature and wait" % bed_temperature + n_l
    gcode += "G21                             ;metric values" + n_l
    gcode += "G90                             ;absolute positioning" + n_l
    gcode += "M83                             ;set e-values to relative while in absolute mode" + n_l
    if acceleration != 0:
        gcode += "M201 X" + str(acceleration) + " Y" + str(acceleration) + "          ;set max acceleration in xy" + n_l
    if jerk != 0:
        gcode += "M207 X" + str(jerk) + "            ;set max jerk" + n_l  # TODO: check firmware compatibility of M207
    gcode += "G28 X0 Y0                       ;home x and y axes" + n_l
    gcode += "G28 Z0                          ;home z axis independently" + n_l
    gcode += "G1 F4500                        ;set feedrate to 4,500 mm/min (75 mm/s)" + n_l
    # gcode += "G1 Z15.0                        ;move nozzle up 15mm" + n_l
    # gcode += "G1 F140 E10                     ;extruded slowly some filament (default: 10mm)" + n_l
    # gcode += "G92 E0                          ;reset the extruded length" + n_l  # useless after M83, otherwise needed
    gcode += "G1 F%d                          ;set initial Feedrate" % feedrate_travel + n_l
    gcode += "M117 compas gcode print...      ;show up text on LCD" + n_l
    gcode += ";" + n_l
    # ______________________________________________________________________/ header

    # ######################################################################
    # print dummy line to avoid initially extruded filament to mess up the print (default in CURA slicer)

    h = 0.0  # get the layer height of the 1st printpoint
    for ppt in print_organizer.printpoints_iterator():
        h = ppt.layer_height
        if h:
            break

    gcode += "; Dummy line" + n_l
    # gcode += "G92 E0                               ;Reset Extruder" + n_l
    gcode += "G1 Z2.0 F3000                        ;Move Z Axis up" + n_l
    gcode += "G1 X5.1 Y10 Z%.3f F5000.0            ;Move to start position" % (h * 0.5) + n_l
    gcode += "G1 X5.1 Y150.0 Z%.3f F1500.0 E15     ;Draw the first line" % (h * 0.5) + n_l
    gcode += "G1 X5.4 Y150.0 Z%.3f F5000.0         ;Move to side a little" % (h * 0.5) + n_l
    gcode += "G1 X5.4 Y20 Z%.3f F1500.0 E30        ;Draw the second line" % (h * 0.5) + n_l
    gcode += "G92 E0                               ;Reset Extruder" + n_l
    gcode += "G1 Z2.0 F3000                        ;Move Z Axis up" + n_l
    gcode += ";" + n_l
    # ______________________________________________________________________/ dummy line

    # ######################################################################
    # global parameters
    # retraction_on = True  # boolean; is true when retraction is toggled
    fan_on = False  # boolean; is true when fan is toggled
    prev_point = PrintPoint(Point(0, 0, 0), layer_height=1.0,
                            mesh_normal=Vector(1.0, 0.0, 0.0))  # dummy print_point that is overwritten
    # ______________________________________________________________________/ global parameters

    # ######################################################################
    # iterate all layers, paths
    for point_v, i, j, k in print_organizer.printpoints_indices_iterator():
        pt = point_v.pt
        layer_height = point_v.layer_height
        # Calculate relative length
        re_l = distance_point_point(pt, prev_point.pt)

        if k == 0:  # 'First point
            # retract before moving to first point in path if necessary
            if retraction_min_travel < re_l:
                gcode += "G1 F%d      ;set retraction feedrate" % feedrate_retraction + n_l
                gcode += "G1 E-%d     ;retract" % retraction_length + n_l
                # ZHOP
                gcode += "G1 Z%.3f     ;z-hop" % (prev_point.pt.z + z_hop) + n_l
                # move to first point in path:
                gcode += "G1 F%d     ;set travel feedrate" % feedrate_travel + n_l
                if prev_point.pt.z != pt.z:
                    gcode += "G1 X%.3f Y%.3f Z%.3f" % (pt.x, pt.y, pt.z) + n_l
                else:
                    gcode += "G1 X%.3f Y%.3f" % (pt.x, pt.y) + n_l
                # reverse z-hop after reaching the first point
                gcode += "G1 F%d     ;set retraction feedrate" % feedrate_retraction + n_l
                gcode += "G1 Z%.3f     ;reverse z-hop" % pt.z + n_l
                # reverse retract after reaching the first point
                gcode += "G1 E%d     ;reverse retraction" % retraction_length + n_l
            else:
                if prev_point.pt.z != pt.z:
                    gcode += "G1 X%.3f Y%.3f Z%.3f" % (pt.x, pt.y, pt.z) + n_l
                else:
                    gcode += 'G1 X%.3f Y%.3f' % (pt.x, pt.y) + n_l

            # set extrusion feedrate: low for adhesion to bed and normal otherwise
            if pt.z < min_over_z:
                gcode += "G1 F%d     ;set low feedrate" % feedrate_low + n_l
            else:
                gcode += "G1 F%d     ;set extrusion feedrate" % feedrate + n_l

        else:  # from 2nd point in each path onwards
            # tmpflow = myflow.Branch(b)(i) here we can set the flow multiplier
            # Calculate feedrate : TODO: just a basic formula for now, better ones in the future
            e_val = 4 * re_l * layer_height * path_width / (math.pi * (filament_diameter ** 2))
            if pt.z < min_over_z:
                e_val *= flow_over
            gcode += 'G1 X%.3f Y%.3f E%.3f' % (pt.x, pt.y, e_val) + n_l
        prev_point = point_v

        if fan_on is False:
            if pt.z >= fan_start_z:  # 'Fan On:
                gcode += "M106 S%d     ;set fan on to set speed" % fan_speed + n_l
                fan_on = True

    # 'retract after last path
    gcode += "G1 F%d        ;set ret spd" % feedrate_retraction + n_l
    gcode += "G1 E-%d       ;ret fil" % retraction_length + n_l
    gcode += "G1 Z%.3f      ;ZHop" % (prev_point.pt.z + 5 * z_hop) + n_l
    gcode += "G1 F%d        ;set ret spd" % feedrate_travel + n_l

    #######################################################################
    # Footer
    gcode += "M201 X500 Y500              ;set acceleration to 500mm/s^2" + n_l
    gcode += "G1 F 1000                   ;set feedrate to 1000 mm/min" + n_l
    gcode += "G1 X0 Y0                    ;home x and y axes" + n_l
    gcode += "M104 S0                     ;turn extruder heater off" + n_l
    gcode += "M140 S0                     ;turn bed heater off (if it exists)" + n_l
    gcode += "M84                         ;turn steppers off" + n_l
    gcode += "M106 S0                     ;turn fan off" + n_l
    # ______________________________________________________________________/ footer

    return gcode
