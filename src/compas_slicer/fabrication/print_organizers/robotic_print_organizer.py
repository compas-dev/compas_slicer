import compas_slicer
import logging
from compas_slicer.fabrication.print_organizers.print_organizer import PrintOrganizer
from compas.geometry import Frame, norm_vector, Vector
import math

logger = logging.getLogger('logger')

__all__ = ['RoboticPrintOrganizer']


#############################################
### RoboticPrintOrganizer
#############################################

class RoboticPrintOrganizer(PrintOrganizer):
    """
    Creates fabrication data for robotic 3D printing.
    """

    def __init__(self, slicer, machine_model, extruder_toggle_type="always_on"):
        assert isinstance(machine_model, compas_slicer.fabrication.machine_model.RobotPrinter), \
            "Machine Model does not represent a robot"
        PrintOrganizer.__init__(self, slicer, machine_model, extruder_toggle_type)

    def get_tcp_RCS(self, frame):
        frame = Frame(frame.point, frame.yaxis,
                      frame.zaxis)  # In UR the Z of the frame points down the end effector axis
        tcp_RCS = self.machine_model.robot.from_tcf_to_t0cf([frame])[0]
        return tcp_RCS

    def get_printpoint_neighboring_items(self, layer_key, path_key, i):
        neighboring_items = []
        if i > 0:
            neighboring_items.append(self.printpoints_dict[layer_key][path_key][i - 1])
        else:
            neighboring_items.append(None)
        if i < len(self.printpoints_dict[layer_key][path_key]) - 1:
            neighboring_items.append(self.printpoints_dict[layer_key][path_key][i + 1])
        else:
            neighboring_items.append(None)
        return neighboring_items

    def generate_robotic_commands_dict(self):
        commands = {}

        assert self.printpoints_dict['layer_0']['path_0'][0].velocity, \
            "Attention! You forgot to set the velocity of the printpoints"

        count = 0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for i, printpoint in enumerate(self.printpoints_dict[layer_key][path_key]):
                    tcp_RCS = self.get_tcp_RCS(printpoint.print_frame)
                    neighboring_items = self.get_printpoint_neighboring_items(layer_key, path_key, i)

                    commands[count] = {}
                    commands[count]["x"] = -tcp_RCS.point[0]  # transform from Rhino coordinates to UR5 coordinates
                    commands[count]["y"] = -tcp_RCS.point[1]  # transform from Rhino coordinates to UR5 coordinates
                    commands[count]["z"] = tcp_RCS.point[2]
                    commands[count]["ax"] = -tcp_RCS.axis_angle_vector[0]
                    commands[count]["ay"] = -tcp_RCS.axis_angle_vector[1]
                    commands[count]["az"] = tcp_RCS.axis_angle_vector[2]
                    commands[count]["velocity"] = printpoint.velocity
                    commands[count]["radius"] = get_radius(printpoint, neighboring_items)
                    commands[count]["wait_time"] = printpoint.wait_time
                    commands[count]["extruder_toggle"] = printpoint.extruder_toggle

                    count += 1
        
        logger.info("Generated %d robotic commands" % count)

        return commands


#############################
### Blend radius
#############################

def get_radius(printpoint, neighboring_items):
    d_fillet = 10.0
    buffer_d = 0.3
    radius = d_fillet
    if neighboring_items[0]:
        radius = min(radius,
                     norm_vector(Vector.from_start_end(neighboring_items[0].pt, printpoint.print_frame.point)) * buffer_d)
    if neighboring_items[1]:
        radius = min(radius,
                     norm_vector(Vector.from_start_end(neighboring_items[1].pt, printpoint.print_frame.point)) * buffer_d)

    radius = round(radius, 5)
    return radius


if __name__ == "__main__":
    pass
