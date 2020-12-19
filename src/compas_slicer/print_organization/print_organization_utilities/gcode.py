import logging
from compas_slicer.parameters import get_param

logger = logging.getLogger('logger')

__all__ = ['create_gcode_text']


def create_gcode_text(printpoints_dict, parameters):
    """ Creates a gcode text file
    Parameters
    ----------
    printpoints_dict: dict printpoints information
    parameters : dict with gcode parameters

    Returns
    ----------
    str, gcode text file
    """
    logger.info('Generating gcode')
    gcode = ''

    # get all the necessary parameters:
    z_hop = get_param(parameters, key='z_hop', defaults_type='gcode')
    extruder_temp = get_param(parameters, key='extruder_temperature', defaults_type='gcode')
    bed_temp = get_param(parameters, key='bed_temperature', defaults_type='gcode')
    # ....

    # Iterate through the printpoints_dict and add information to the gcode str
    for layer_key in printpoints_dict:
        for path_key in printpoints_dict[layer_key]:
            pass
            # .... gcode += 'command'
    # Thanks!

    return gcode
