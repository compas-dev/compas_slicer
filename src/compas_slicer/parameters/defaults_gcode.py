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
        'nozzle_diameter': 0.4,  # in mm
        'filament diameter': 1.75,  # in mm, for calculating E
        'delta': False,  # boolean for delta printers
        'print_volume_x': 300,  # in mm
        'print_volume_y': 300,  # in mm
        'print_volume_z': 600,  # in mm

        # Dimensional parameters
        'layer_width': 0.6,  # in mm

        # Temperature parameters
        'extruder_temperature': 200,  # in °C
        'bed_temperature': 60,  # in °C
        'fan_speed': 255,  # 0-255
        'fan_start_z': 0,  # in mm; height at which the fan starts

        # Movement parameters
        'flowrate': 1,  # as fraction; this is a global flow multiplier
        'feedrate': 3600,  # in mm/s
        'feedrate_travel': 4800,  # in mm/s
        'feedrate_low': 1800,  # in mm/s
        'feedrate_retraction': 2400,  # in mm/s
        'acceleration': 0,  # in mm/s²; if set to 0, the default driver value will be used
        'jerk': 0,  # in mm/s; if set to 0, the default driver value will be used

        # Retraction
        'z_hop': 0.5,  # in mm
        'retraction_length': 1,  # in mm
        'retraction_min_travel': 6,  # in mm; below this value, retraction does not happen

        # Adhesion parameters
        'flow_over': 1,  # as fraction, usually > 1; overextrusion value for z < min_over_z, for better adhesion
        'min_over_z': 0,  # in mm; for z < min_over_z, the overextrusion factor applies
    }
