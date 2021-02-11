__all__ = ['print_organization_default_param']


def print_organization_default_param(key):
    """ Returns the default parameters with the specified key. """
    if key in default_parameters:
        return default_parameters[key]
    else:
        raise ValueError('The parameter with key : ' + str(key) +
                         ' does not exist in the defaults of curved_slicing parameters. ')


default_parameters = \
    {
        'layer_heights_smoothing': [False, 5, 0.2],
        'up_vectors_smoothing': [True, 2, 0.2],
    }
