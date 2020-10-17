__all__ = ['set_extruder_toggle']


def set_extruder_toggle(printpoints_dict, extruder_toggle_type):
    if not (extruder_toggle_type == "continuous_shell_printing"
            or extruder_toggle_type == "interrupt_between_paths"):
        raise ValueError("Extruder toggle method doesn't exist")

    for layer_key in printpoints_dict:
        for path_key in printpoints_dict[layer_key]:
            path_printpoints = printpoints_dict[layer_key][path_key]
            for i, printpoint in enumerate(path_printpoints):
                if extruder_toggle_type == "continuous_shell_printing":  # single shell printing
                    printpoint.extruder_toggle = True
                # elif extruder_toggle_type == "always_off":
                #     printpoint.extruder_toggle_type = False
                elif extruder_toggle_type == "interrupt_between_paths":  # multiple contours
                    if i == len(path_printpoints) - 1:
                        printpoint.extruder_toggle = False
                    else:
                        printpoint.extruder_toggle = True

        # set extruder toggle of last print point to false
        last_layer_key = 'layer_%d' % (len(printpoints_dict) - 1)
        last_path_key = 'path_%d' % (len(printpoints_dict[last_layer_key]) - 1)
        printpoints_dict[last_layer_key][last_path_key][-1].extruder_toggle = False
