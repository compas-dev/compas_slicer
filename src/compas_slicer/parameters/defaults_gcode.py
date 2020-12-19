__all__ = ['gcode_param']


def gcode_param(key):
    """ Returns the parameters with the specified key. """
    if key in default_parameters:
        return default_parameters[key]
    else:
        raise ValueError('The parameter with key : ' + str(key) +
                         ' does not exist in the defaults of gcode parameters. ')


default_parameters = \
    {
        'z_hop': 0.5
    }
