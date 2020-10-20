import compas_slicer

__all__ = ['set_extruder_toggle']


def set_extruder_toggle(printpoints_dict, slicer):
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
