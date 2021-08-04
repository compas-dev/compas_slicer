from compas.geometry import Vector, dot_vectors
from compas_slicer.utilities import remap, remap_unbound
import logging

logger = logging.getLogger('logger')

__all__ = ['set_linear_velocity_constant',
           'set_linear_velocity_per_layer',
           'set_linear_velocity_by_range',
           'set_linear_velocity_by_overhang']


def set_linear_velocity_constant(print_organizer, v=25.0):
    """Sets the linear velocity parameter of the printpoints depending on the selected type.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    v:  float. Velocity value (in mm/s) to set for printpoints. Defaults to 25 mm/s.
    """

    logger.info("Setting constant linear velocity")
    for printpoint in print_organizer.printpoints_iterator():
        printpoint.velocity = v


def set_linear_velocity_per_layer(print_organizer, per_layer_velocities):
    """Sets the linear velocity parameter of the printpoints depending on the selected type.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    per_layer_velocities: list
        A list of velocities (floats) with equal length to the number of layers.
    """

    logger.info("Setting per-layer linear velocity")
    assert len(per_layer_velocities) == print_organizer.number_of_layers, 'Wrong number of velocity values. You need \
        to provide one velocity value per layer, on the "per_layer_velocities" list.'
    for printpoint, i, j, k in print_organizer.printpoints_indices_iterator():
        printpoint.velocity = per_layer_velocities[i]


def set_linear_velocity_by_range(print_organizer, param_func, parameter_range, velocity_range,
                                 bound_remapping=True):
    """Sets the linear velocity parameter of the printpoints depending on the selected type.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    param_func: function that takes as argument a :class: 'compas_slicer.geometry.Printpoint': get_param_func(pp)
        and returns the parameter value that will be used for the remapping
    parameter_range: tuple
        An example of a parameter that can be used is the overhang angle, or the layer height.
    velocity_range: tuple
        The range of velocities where the parameter will be remapped
    bound_remapping: bool
        If True, the remapping is bound in the domain velocity_range, else it is unbound.
    """

    logger.info("Setting linear velocity based on parameter range")
    for printpoint in print_organizer.printpoints_iterator():
        param = param_func(printpoint)
        assert param, 'The param_func does not return any value for calculating the velocity range.'
        if bound_remapping:
            v = remap(param, parameter_range[0], parameter_range[1], velocity_range[0], velocity_range[1])
        else:
            v = remap_unbound(param, parameter_range[0], parameter_range[1], velocity_range[0], velocity_range[1])
        printpoint.velocity = v


def set_linear_velocity_by_overhang(print_organizer, overhang_range, velocity_range, bound_remapping=True):
    """Set velocity by overhang by using set_linear_velocity_by_range.

    An example function for how to use the 'set_linear_velocity_by_range'. In this case the parameter that controls the
    velocity is the overhang, measured as a dot product with the horizontal direction.

    Parameters
    ----------
    print_organizer: :class:`compas_slicer.print_organization.BasePrintOrganizer`
    overhang_range: tuple:
        should be within [0.0, 1.0]. For example a reasonable value would be [0.0, 0.5], that would
        be remapping overhangs up to 45 degrees
    velocity_range: tuple
    bound_remapping: bool
    """

    def param_func(ppt): return dot_vectors(ppt.mesh_normal, Vector(0.0, 0.0, 1.0))
    # returns values from 0.0 (no overhang) to 1.0 (horizontal overhang)
    set_linear_velocity_by_range(print_organizer, param_func, overhang_range, velocity_range, bound_remapping)


if __name__ == "__main__":
    pass
