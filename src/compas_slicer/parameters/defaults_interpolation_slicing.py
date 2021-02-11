__all__ = ['interpolation_slicing_default_param']


def interpolation_slicing_default_param(key):
    """ Returns the default parameters with the specified key. """
    if key in default_parameters:
        return default_parameters[key]
    else:
        raise ValueError('The parameter with key : ' + str(key) +
                         ' does not exist in the defaults of curved_slicing parameters. ')


default_parameters = \
    {
        'target_LOW_smooth_union': [False, 0],
        'target_LOW_geodesics_method': 'exact_igl',
        'target_HIGH_smooth_union': [False, 0],
        'target_HIGH_geodesics_method': 'exact_igl',
        'uneven_upper_targets_offset': 0,
    }
