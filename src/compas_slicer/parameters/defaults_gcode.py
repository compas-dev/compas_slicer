__all__ = ['gcode_default_param']


def gcode_default_param(key):
    """ Returns the default parameter with the specified key. """
    if key in default_parameters:
        return default_parameters[key]
    else:
        raise ValueError('The parameter with key : ' + str(key) +
                         ' does not exist in the defaults of gcode parameters. ')


default_parameters = \
    {
        # Physical parameters
        'delta': False,  # boolean for delta printers
        'nozzle_diameter': 0.4,  # in mm
        'filament diameter': 1.75,  # in mm, for calculating E

        # Dimensional parameters
        'layer_width': 0.6,  # in mm

        'flow_over' : 0.0,
        'min_over_z' : 0.0,

        # Temperature parameters
        'extruder_temperature': 200,  # in °C
        'bed_temperature': 60,  # in °C
        'fan_speed': 255,  # 0-255
        'fan_start_z': 0,  # in mm; height at which the fan starts

        # Movement parameters
        'feedrate': 3600,  # in mm/s
        'feedrate_travel': 4800,  # in mm/s
        'feedrate_low': 1800,  # in mm/s
        'feedrate_retraction': 3600,  # in mm/s
        # 'acceleration': 3600, #in mm/s²
        # 'jerk': 3600, #in mm/s

        # Retraction
        'z_hop': 0.5,  # in mm
        'retraction_length': 1,  # in mm
        'retraction_min_travel': 3,  # in mm; below this value, retraction does not happen
    }
