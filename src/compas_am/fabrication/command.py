import os
import json



class RobotCommand(Command):
    def __init__(self):
        Command.__init__(self) 
        self.robot_configuration = None 
        self.wait_time = wait_time

    def get_command_dict(self):
        pass


class FDMPrinterCommand(Command):


class Command(object):
    def __init__(self, add, parameters, here):
        self.machine_model = machine_model
        self.plane = plane
        self.extruder_toggle = extruder_toggle
        self.radius = radius
        self.linear_velocity = None 
        


if __name__ == "__main__":
    pass