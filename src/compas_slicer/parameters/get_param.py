import compas_slicer

__all__ = ['get_param']


def get_param(params, key, defaults_type):
    """
    Function useful for accessing the params dictionary of curved slicing.
    If the key is in the params dict, it returns its value,
    otherwise it returns the default_value.

    Parameters
    ----------
    params: dict
    key: str
    defaults_type: str specifying which defaults the dictionary of parameters draws for. 'curved_slicing' / 'gcode'

    Returns
    ----------
    params[key] if key in params, otherwise default_value
    """
    if key in params:
        return params[key]
    else:
        if defaults_type == 'interpolation_slicing':
            return compas_slicer.parameters.interpolation_slicing_default_param(key)
        elif defaults_type == 'gcode':
            return compas_slicer.parameters.gcode_default_param(key)
        elif defaults_type == 'layers':
            return compas_slicer.parameters.layers_default_param(key)
        elif defaults_type == 'print_organization':
            return compas_slicer.parameters.gcode_default_param(key)
        else:
            raise ValueError('The specified parameter type : ' + str(defaults_type) + ' does not exist.')
