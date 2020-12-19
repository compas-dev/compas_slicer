import logging
from compas_slicer.parameters import get_param

logger = logging.getLogger('logger')

__all__ = ['create_gcode_text']


def create_gcode_text(printpoints_dict, parameters):
    """ Creates a gcode text file
    Parameters
    ----------
    printpoints_dict: dict with compas_slicer.geometry.Printpoint instances.
        The keys of the dictionary are setup in the following way:
        {['layer_%d' % i] =
            {['path_%d' % i] =
                [printpoint_1 , ....., printpoint_n ]
            }
        }
    parameters : dict with gcode parameters.
        The defaults for those parameters are in the file compas_slicer.parameters.defaults_gcode.

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

            gcode += 'this is a command %.4f %.4f %.4f \n' % (z_hop, extruder_temp, bed_temp)  # just remove this line

            # .... gcode += 'command'
    # Thanks!

    return gcode
