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
        'extruder_temperature': 200,
        'bed_temperature': 60,
        'z_hop': 0.5,
        # add more parameters as you see fit
    }