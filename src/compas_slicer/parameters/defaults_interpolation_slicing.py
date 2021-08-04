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
        # geodesics method
        'target_LOW_geodesics_method': 'exact_igl',
        'target_HIGH_geodesics_method': 'exact_igl',

        # union method for HIGH target
        # if all are false, then default 'min' method is used
        'target_HIGH_smooth_union': [False, [10.0]],  # blend radius
        'target_HIGH_chamfer_union': [False, [100.0]],  # size
        'target_HIGH_stairs_union': [False, [80.0, 3]],  # size, n-1 number of peaks

        'uneven_upper_targets_offset': 0,

    }
