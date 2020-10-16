import logging

logger = logging.getLogger('logger')

__all__ = ['generate_gcode']

def generate_gcode(printpoints_dict, FILE, machine_model, material):
    """Creates all the commands in order for print_organization

    Attributes
    ----------
    paths: list
        compas_slicer.geometry.Layer or any class inheriting from it
    FILE : str
        Path of gcode file to be saved.
    machine_model : The class that stores the information for the 3d printer
        compas_slicer.print_organization.MachineModel
    
    GCODE COMMANDS (for reference)

    G28                     - Home all axes
    G29                     - Bed Leveling (Automatic)
    G28 X Y                 - Home X and Y axes
    G90                     - Set Absolute Positioning (movement)
    M82                     - Set Absolute Extrusion mode (extrusion)
    G0                      - Travel move (non-extrusion)
    G1 X0 Y0 F2400          - Linear Movement, move to X = 0, Y = 0 with a speed of 2400 mm/min
    G1 X20 Y20 E10 F1200    - Linear Movement, move to X = 20, Y = 20 with a speed of 1200 mm/min while pushing 10mm of filament (E)
    G92 E0                  - Set current filament position to E=0. Can also be used for X, Y, Z axes
    M104 S190 T0            - Start heating T0 to 190 degrees celcius
    M109 S190 T0            - Wait until T0 is 190 degrees before continuing commands
    M116                    -
    M140 S50                - Heat the bed to 50 degrees celcius
    M190                    - Wait until the bed is 50 degrees before continuing
    M106 255                - Set Fan Speed (255 = fully on, 0 = off)
    M73 P25                 - Set current print progress for LCD screen to 25%
    
    """

    ## print parameters coming from machine model
    extruder_temp = material.parameters["extruder_temperature"]
    bed_temp = material.parameters["bed_temperature"]
    print_speed = material.parameters["print_speed"]
    z_hop = material.parameters["z_hop"]

    filament_feed_length = 0  ## Shouldn't this also be coming from machine_model print_parameters?

    # convert print_speed mm/s to mm/min
    print_speed = print_speed * 60
    layer_number = 1  # start count

    with open(FILE, "w") as f:
        f.write("; Generated by compas_slicer vX.X\n")
        f.write("; LAYER HEIGHT: \n")

        f.write("M201 X1000 Y1000 Z1000 E5000 ; sets max acceleration mm/sec^2\n")
        f.write("M203 X200 Y200 Z12 E120 ; sets max feedrates, mm/sec\n")

        f.write("M83; extruder relative mode\n")

        f.write("M104 S{0} ; set extruder temperature\n".format(extruder_temp))  # extruder_temperature
        f.write("M140 S{0} ; set bed temperature\n".format(bed_temp))  # bed_temperature
        f.write("M190 S{0} ; wait for bed temperature\n".format(bed_temp))  # bed_temperature

        f.write("G28 ; home all axes without mesh bed level\n")
        f.write("G80 ; mesh bed leveling\n")

        f.write("G1 Y-3.0 F1000.0 ; go outside print area\n")
        f.write("G92 E0 ; set filament pos to 0\n")
        f.write("G1 X60.0 E9.0 F1000 ; intro line\n")
        f.write("M73 P0 R{0} ; set progress to 0 and time remaining to total time\n".format(
            000))  # 000 to be replaced by remaining time
        f.write("M73 Q0 R{0} ; set progress to 0 and time remaining to total time for quiet mode\n".format(
            000))  # 000 to be replaced by remaining time
        f.write("G1 X100 E12.5 F1000 ; intro line\n")

        f.write("G92 E0 ; set filament pos to 0\n")
        f.write("G21 ; set units to millimeters\n")
        f.write("G90 ; use absolute coordinates\n")
        f.write("M83 ; use relative distances for extrusion\n")

        f.write("G1 F{0} ; set print speed\n".format(print_speed))

        for layer_key in printpoints_dict:
            logger.debug("Gcode layer number : %d" % layer_number)
            f.write(";LAYER:{0}\n".format(layer_number))

            for path_key in printpoints_dict[layer_key]:
                for i, printpoint in enumerate(printpoints_dict[layer_key][path_key]):
                    point = printpoint.pt
                    filament_feed_length = get_filament_feed_length(printpoint, i, layer_key, path_key, printpoints_dict)  ## TODO!
                    f.write("G1 X{x} Y{y} Z{z} E{e}\n".format(x=point[0],
                                                              y=point[1],
                                                              z=point[2],
                                                              e=filament_feed_length))

            layer_number += 1

        logger.info("Saved to gcode: " + FILE)


def get_filament_feed_length(printpoint, i, layer_key, path_key, printpoints_dict):
    return 0
    # if printpoint.extruder_toggle_type and i < len(printpoints)-1:
    #     next_point = printpoints[i+1]
    #     # TODO!!!
    #     return 0
    # else:
    #     return 0
