__all__ = ['set_wait_time']


def set_wait_time(printpoints_dict, wait_time_value):
    """Sets the wait_time value for the printpoints.

    Parameters
    ----------
    printpoints_dict: dictionary of :class:`compas.slicer.geometry.PrintPoint`
        Dictionary of PrintPoints.
    wait_time_value: float
        Value (in seconds) to wait at printpoint.
    """

    for layer_key in printpoints_dict:
        for path_key in printpoints_dict[layer_key]:
            path_printpoints = printpoints_dict[layer_key][path_key]
            for printpoint in path_printpoints:
                printpoint.wait_time = wait_time_value
