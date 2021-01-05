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
        # These parameters are not thought-through! Feel free to change them as you see fit
    
        # Physical parameters
        'delta': False, #boolean for delta printers
        'nozzle_diameter': 0.4, #in mm
        'filament diameter': 1.75, #in mm, for calculating E
    
        # Dimensional parameters
        'layer width': 0.6, #in mm
    
        # Temperature parameters
        'extruder_temperature': 200, #in °C
        'bed_temperature': 60, #in °C
        'fan_speed': 255, #0-255
        'fan_start_z': 0, #in mm; height at which the fan starts
    
    
        'z_hop': 0.5, #in mm
        # add more parameters as you see fit
    }
