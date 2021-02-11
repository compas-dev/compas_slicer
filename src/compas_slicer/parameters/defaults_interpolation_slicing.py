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
        'avg_layer_height': 5.0,
        'max_layer_height': 50.0,
        'min_layer_height': 0.1,
        'target_LOW_smooth_union': [False, 0],
        'target_LOW_geodesics_method': 'exact_igl',
        'target_HIGH_smooth_union': [False, 0],
        'target_HIGH_geodesics_method': 'exact_igl',
        'uneven_upper_targets_offset': 0,
        'layer_heights_smoothing': [False, 5, 0.2],
        'up_vectors_smoothing': [True, 2, 0.2],
        'vertical_layers_max_centroid_dist': 25.0
    }
