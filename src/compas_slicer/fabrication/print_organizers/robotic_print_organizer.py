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
                    commands[count]["velocity"] = calculate_robot_linear_velocity(printpoint)
                    commands[count]["radius"] = get_radius(printpoint, neighboring_items)
                    commands[count]["wait_time"] = printpoint.wait_time
                    commands[count]["extruder_toggle"] = printpoint.extruder_toggle
                    count += 1
        
        logger.info("Generating %d robotic commands" % count)

        return commands


#############################
### Robot linear velocity
#############################

motor_omega = 2 * math.pi  # 1 revolution / sec = 2*pi rad/sec
motor_r = 4.0  # 4.25 #mm
motor_linear_speed = motor_omega * motor_r
D_filament = 2.75  # mm
filament_area = math.pi * (D_filament / 2.0) ** 2  # pi*r^2

multiplier = 0.25  # arbitrary value! You might have to change this


# path_area * robot_linear_speed = filament_area * motor_linear_speed

def calculate_robot_linear_velocity(printpoint):
    layer_width = max(printpoint.layer_height, 0.4)
    path_area = layer_width * printpoint.layer_height
    robot_linear_speed = (filament_area * motor_linear_speed) / path_area
    return robot_linear_speed * multiplier


#############################
### Blend radius
#############################

def get_radius(printpoint, neighboring_items):
    dfillet = 10.0
    buffer_d = 0.5
    radius = 0.0
    if neighboring_items[0]:
        radius = min(radius,
                     norm_vector(Vector.from_start_end(neighboring_items[0].pt, printpoint.print_frame.point)) * 0.5 * buffer_d)
    if neighboring_items[1]:
        radius = min(radius,
                     norm_vector(Vector.from_start_end(neighboring_items[1].pt, printpoint.print_frame.point)) * 0.5 * buffer_d)

    radius = round(radius, 5)
    return radius


if __name__ == "__main__":
    pass
