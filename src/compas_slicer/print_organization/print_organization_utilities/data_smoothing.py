import logging
from copy import deepcopy

logger = logging.getLogger('logger')

__all__ = ['smooth_printpoint_attribute',
           'smooth_printpoints_up_vectors',
           'smooth_printpoints_layer_heights']


def smooth_printpoint_attribute(print_organizer, iterations, strength, get_attr_value, set_attr_value):
    """
    Iterative smoothing of the printpoints attribute.
    The attribute is accessed using the function 'get_attr_value(ppt)', and is set using the function
    'set_attr_value(ppt, v)'.
    All attributes are smoothened continuously (i.e. as if their printpoints belong into one long uninterrupted path)
    For examples of how to use this function look at 'smooth_printpoints_layer_heights' and
    'smooth_printpoints_up_vectors' below.
    The smoothing is happening by taking an average of the previous and next point attributes, and combining them with
    the current value of the print point; On every iteration:
    new_val = (0.5*(neighbor_left_val + neighbor_right_attr)) * strength - current_val * (1-strength)

    Parameters
    ----------
    print_organizer: :class: 'compas_slicer.print_organization.BasePrintOrganizer', or other class inheriting from it.
    iterations: int, smoothing iterations
    strength: float. in the range [0.0 - 1.0]. 0.0 corresponds to no smoothing at all, 1.0 corresponds to overwriting
        the current value with the average of the two neighbors on every interation stop. On each iteration:
        new_val = (0.5*(neighbor_left_val + neighbor_right_attr)) * strength - current_val * (1-strength)
    get_attr_value: function that returns an attribute of a printpoint, get_attr_value(ppt)
    set_attr_value: function that sets an attribute of a printpoint, set_attr_value(ppt, new_value)
    """

    # first smoothen the values
    for ppt in print_organizer.printpoints_iterator():
        assert get_attr_value(ppt), 'The attribute you are trying to smooth has not been assigned a value'

    attrs = [get_attr_value(ppt) for ppt in print_organizer.printpoints_iterator()]
    new_values = deepcopy(attrs)

    for iteration in range(iterations):
        for i, ppt in enumerate(print_organizer.printpoints_iterator()):
            if 0 < i < len(attrs) - 1:  # ignore first and last element
                mid = (attrs[i - 1] + attrs[i + 1]) * 0.5
                new_values[i] = mid * strength + attrs[i] * (1 - strength)
        attrs = new_values

        # in the end assign the new (smoothened) values to the printpoints
        if iteration == iterations - 1:
            for i, ppt in enumerate(print_organizer.printpoints_iterator()):
                set_attr_value(ppt, attrs[i])


def smooth_printpoints_layer_heights(print_organizer, iterations, strength):
    """ This function is an example for how the 'smooth_printpoint_attribute' function can be used. """

    def get_ppt_layer_height(printpoint):
        return printpoint.layer_height  # get value

    def set_ppt_layer_height(printpoint, v):
        printpoint.layer_height = v  # set value

    smooth_printpoint_attribute(print_organizer, iterations, strength, get_ppt_layer_height, set_ppt_layer_height)


def smooth_printpoints_up_vectors(print_organizer, iterations, strength):
    """ This function is an example for how the 'smooth_printpoint_attribute' function can be used. """

    def get_ppt_up_vec(printpoint):
        return printpoint.up_vector  # get value

    def set_ppt_up_vec(printpoint, v):
        printpoint.up_vector = v  # set value

    smooth_printpoint_attribute(print_organizer, iterations, strength, get_ppt_up_vec, set_ppt_up_vec)
    # finally update any values in the printpoints that are affected by the changed attribute
    for ppt in print_organizer.printpoints_iterator():
        ppt.frame = ppt.get_frame()
