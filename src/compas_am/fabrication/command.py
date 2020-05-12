import os
import json

class Command(object):
    def __init__(self, add, parameters, here):
        self.machine_model = machine_model
        self.plane = plane
        self.extruder_toggle = extruder_toggle
        self.wait_time = wait_time
        self.radius = radius

        self.linear_velocity = None 

        self.time = None

        self.machine_configuration = None 

    

    def get_fabrication_command_dict(self):
        command = {}
        command["x"] = -self.tcp_RCS.point[0] #transform from Rhino coordinates to UR5 coordinates
        command["y"] = -self.tcp_RCS.point[1] #transform from Rhino coordinates to UR5 coordinates
        command["z"] = self.tcp_RCS.point[2]
        command["ax"] = -self.tcp_RCS.axis_angle_vector[0]
        command["ay"] = -self.tcp_RCS.axis_angle_vector[1]
        command["az"] = self.tcp_RCS.axis_angle_vector[2]
        command["velocity"] = self.robot_linear_velocity
        command["time"] = self.time
        command["radius"] = self.radius
        command["wait_time"] = self.wait_time
        command["extruder_toggle"] = self.extruder_toggle

        if self.machine_configuration:
            command["machine_configuration"] = self.machine_configuration.values
        else: 
            command["machine_configuration"] = None
        return command






if __name__ == "__main__":
    pass