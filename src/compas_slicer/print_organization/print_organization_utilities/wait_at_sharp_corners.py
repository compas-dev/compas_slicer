from compas.geometry import Vector, normalize_vector
from compas_slicer.print_organization.print_organization_utilities.extruder_toggle import check_assigned_extruder_toggle
from compas_slicer.utilities import find_next_printpoint
import copy
import logging
import math

logger = logging.getLogger('logger')

__all__ = ['wait_at_sharp_corners']


def wait_at_sharp_corners(print_organizer, threshold=0.4*math.pi, wait_time=0.3):
    for printpoint, i, j, k in print_organizer.printpoints_indices_iterator():
        neighbors = print_organizer.get_printpoint_neighboring_items('layer_%d' % i, 'path_%d' % j, k)
        prev_ppt = neighbors[0]
        next_ppt = neighbors[1]

        if prev_ppt and next_ppt:
            v_to_prev = normalize_vector(Vector.from_start_end(printpoint.pt, prev_ppt.pt))
            v_to_next = normalize_vector(Vector.from_start_end(printpoint.pt, next_ppt.pt))
            a = abs(Vector(*v_to_prev).angle(v_to_next))
            if a < threshold:
                printpoint.wait_time = wait_time
                printpoint.blend_radius = 0.0 # 0.0 blend radius for points where the robot will wait
