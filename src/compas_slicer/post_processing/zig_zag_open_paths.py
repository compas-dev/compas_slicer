from compas.geometry import Vector
from compas_slicer.print_organization.print_organization_utilities.extruder_toggle import check_assigned_extruder_toggle
from compas_slicer.utilities import find_next_printpoint
import copy
import logging

logger = logging.getLogger('logger')

__all__ = ['zig_zag_open_paths']


def zig_zag_open_paths(slicer):
    reverse = False
    for layer in slicer.layers:
        for i, path in enumerate(layer.paths):
            if not path.is_closed:
                if not reverse:
                    reverse = True
                else:
                    path.points.reverse()
                    reverse = False

                path.is_closed = True  # label as closed so that it is printed without interruption
