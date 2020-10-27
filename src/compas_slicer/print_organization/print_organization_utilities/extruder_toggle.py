import compas_slicer

__all__ = ['set_extruder_toggle',
           'override_extruder_toggle']


def set_extruder_toggle(printpoints_dict, slicer):
    """ Sets the extruder toggle value for the printpoints.

    Parameters
    ----------
    printpoints_dict: dictionary of :class:`compas.slicer.geometry.PrintPoint`
        Dictionary of PrintPoints.
    v: float
        Velocity value to set for printpoints.
    velocity_type: str
        Determines how to add linear velocity to the printpoints.

        constant:              one value used for all printpoints
        per_layer:             different values used for every layer
        matching_layer_height: set velocity in accordance to layer height
        matching_overhang:     set velocity in accordance to the overhang
    per_layer_velocities: list of floats
        If setting velocity per layer, provide a list of floats with equal length to the number of layers.

    """

    for i, layer in enumerate(slicer.layers):
        layer_key = 'layer_%d' % i
        is_vertical_layer = isinstance(layer, compas_slicer.geometry.VerticalLayer)

        for j, path in enumerate(layer.paths):
            path_key = 'path_%d' % j
            is_closed_path = path.is_closed

            # --- decide if the path should be interrupted at the end
            interrupt_path = False
            if not is_closed_path:
                interrupt_path = True
                # open paths should always be interrupted

            if not is_vertical_layer and len(layer.paths) > 1:
                interrupt_path = True
                # horizontal layers with multiple paths should be interrupted so that the extruder
                # can travel from one path to the other
                # Note: Maybe an exception should be added here for the first brim layer?

            if is_vertical_layer and j == len(layer.paths) - 1:
                interrupt_path = True
                # the last path of a vertical layer should be interrupted

            # --- create extruder toggles
            path_printpoints = printpoints_dict[layer_key][path_key]
            for k, printpoint in enumerate(path_printpoints):

                if interrupt_path:
                    if k == len(path_printpoints) - 1:
                        printpoint.extruder_toggle = False
                    else:
                        printpoint.extruder_toggle = True
                else:
                    printpoint.extruder_toggle = True

        # set extruder toggle of last print point to false
        last_layer_key = 'layer_%d' % (len(printpoints_dict) - 1)
        last_path_key = 'path_%d' % (len(printpoints_dict[last_layer_key]) - 1)
        printpoints_dict[last_layer_key][last_path_key][-1].extruder_toggle = False


def override_extruder_toggle(printpoints_dict, override_value):
    if isinstance(override_value, bool):
        for layer_key in printpoints_dict:
            for path_key in printpoints_dict[layer_key]:
                path_printpoints = printpoints_dict[layer_key][path_key]
                for printpoint in path_printpoints:
                    printpoint.extruder_toggle = override_value

    else:
        raise NameError("Override value must be of type bool")
