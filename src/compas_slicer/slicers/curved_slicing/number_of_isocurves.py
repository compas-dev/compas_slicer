import logging

logger = logging.getLogger('logger')

__all__ = ['find_desired_number_of_isocurves']


#  --- Find desired number of curves
def find_desired_number_of_isocurves(target_0, target_1, avg_layer_height=1.1):
    """ Returns the average number of isocurves that can cover the distance from target_0 to target_1

    Parameters
    ----------
    target_0: :class: 'compas_slicer.slicing.curved_slicing.CompoundTarget'
    target_1: :class: 'compas_slicer.slicing.curved_slicing.CompoundTarget'
    avg_layer_height: int
    """
    extreme_ds0 = target_0.get_extreme_distances_from_other_target(target_1)
    extreme_ds1 = target_1.get_extreme_distances_from_other_target(target_0)

    number_of_curves = max(max(extreme_ds0), max(extreme_ds1)) / avg_layer_height
    number_of_curves = int(number_of_curves)

    return max(1, number_of_curves)


if __name__ == "__main__":
    pass
