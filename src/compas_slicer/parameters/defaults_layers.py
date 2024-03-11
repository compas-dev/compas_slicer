__all__ = ['layers_default_param']


def layers_default_param(key):
    """ Returns the default parameters with the specified key. """
    if key in default_parameters:
        return default_parameters[key]
    else:
        raise ValueError('The parameter with key : ' + str(key) +
                         ' does not exist in the defaults of curved_slicing parameters. ')


default_parameters = \
    {
        'avg_layer_height': 5.0,
        'vertical_layers_max_centroid_dist': 25.0
    }
