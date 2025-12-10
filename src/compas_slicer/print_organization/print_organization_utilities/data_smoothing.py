from __future__ import annotations

from loguru import logger
from typing import TYPE_CHECKING, Any, Callable

import numpy as np
from compas.geometry import Vector

if TYPE_CHECKING:
    from compas_slicer.geometry import PrintPoint
    from compas_slicer.print_organization import BasePrintOrganizer


__all__ = ['smooth_printpoint_attribute',
           'smooth_printpoints_up_vectors',
           'smooth_printpoints_layer_heights']


def smooth_printpoint_attribute(
    print_organizer: BasePrintOrganizer,
    iterations: int,
    strength: float,
    get_attr_value: Callable[[PrintPoint], Any],
    set_attr_value: Callable[[PrintPoint, Any], None],
) -> None:
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

    attrs = np.array([get_attr_value(ppt) for ppt in print_organizer.printpoints_iterator()])

    # Vectorized smoothing: use numpy slicing instead of per-element loop
    for _ in range(iterations):
        # mid = 0.5 * (attrs[i-1] + attrs[i+1]) for interior points
        mid = 0.5 * (attrs[:-2] + attrs[2:])  # shape: (n-2,)
        # new_val = mid * strength + attrs[1:-1] * (1 - strength)
        attrs[1:-1] = mid * strength + attrs[1:-1] * (1 - strength)

    # Assign the smoothened values back to the printpoints
    for i, ppt in enumerate(print_organizer.printpoints_iterator()):
        val = attrs[i]
        # Convert back from numpy type if needed
        set_attr_value(ppt, val.tolist() if hasattr(val, 'tolist') else float(val))


def smooth_printpoints_layer_heights(
    print_organizer: BasePrintOrganizer, iterations: int, strength: float
) -> None:
    """ This function is an example for how the 'smooth_printpoint_attribute' function can be used. """

    def get_ppt_layer_height(printpoint):
        return printpoint.layer_height  # get value

    def set_ppt_layer_height(printpoint, v):
        printpoint.layer_height = v  # set value

    smooth_printpoint_attribute(print_organizer, iterations, strength, get_ppt_layer_height, set_ppt_layer_height)


def smooth_printpoints_up_vectors(
    print_organizer: BasePrintOrganizer, iterations: int, strength: float
) -> None:
    """ This function is an example for how the 'smooth_printpoint_attribute' function can be used. """

    def get_ppt_up_vec(printpoint):
        return printpoint.up_vector  # get value

    def set_ppt_up_vec(printpoint, v):
        # Convert list back to Vector for proper serialization
        printpoint.up_vector = Vector(*v) if isinstance(v, list) else v

    smooth_printpoint_attribute(print_organizer, iterations, strength, get_ppt_up_vec, set_ppt_up_vec)
    # finally update any values in the printpoints that are affected by the changed attribute
    for ppt in print_organizer.printpoints_iterator():
        ppt.frame = ppt.get_frame()
