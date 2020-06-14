import logging
import compas
import compas_am
from compas.geometry import Box
from compas.datastructures import Mesh
from compas_fab.backends import RosClient
from compas_fab.robots import PlanningScene, Tool

logger = logging.getLogger('logger')

__all__ = ['MachineModel',
           'FDMPrinter',
           'RobotPrinter']


class MachineModel(object):
    """
    Class for representing various fabrication machines (3D printers, robots etc.)
    """

    def __init__(self, id):
        self.id = id
        self.properties = self.get_machine_properties()

    def get_machine_properties(self):
        raise NotImplementedError

    def get_machine_dimensions(self):
        return self.properties["x_bounds"], self.properties["y_bounds"], self.properties["z_bounds"]

    def get_machine_bounding_box(self):
        bbox = Box.from_corner_corner_height((0, 0, 0), (self.properties["x_bounds"], self.properties["y_bounds"], 0),
                                             self.properties["z_bounds"])
        return bbox

    def set_machine_property(self, name, value):
        self.properties[name] = value

    def load_machine_properties_from_json(self):
        pass  # TODO!

    def save_machine_properties_to_json(self):
        pass  # TODO!

    def printout_info(self):
        print("\n---- Machine Model Info ----")
        print("ID : ", self.id)
        print("Properties : ")
        print(self.properties)
        print("")


##############################
#### FDM 3D printer
##############################

class FDMPrinter(MachineModel):
    """
    Class for representing FDM 3D printers.
    """

    def __init__(self, id):
        MachineModel.__init__(self, id)

    def get_machine_properties(self):
        properties = {}

        if self.id == "FDM_Prusa_i3_mk2":
            properties = {
                "x_bounds": 250,
                "y_bounds": 210,
                "z_bounds": 200
            }

        else:
            logger.warning("Unknown printer : " + self.id)
        return properties


##############################
#### Robot 3D printer
##############################

class RobotPrinter(MachineModel):
    """
    Class for representing Robotic printers
    """

    def __init__(self, id, IP=None):
        MachineModel.__init__(self, id)

        self.robot, self.scene = self.get_robot_model(IP)  # compas robot

        ## print parameters
        self.properties = self.get_machine_properties()

    def get_machine_properties(self):
        properties = {}

        if self.id == "UR5":
            properties = {
                "x_bounds": 0,  # TODO
                "y_bounds": 0,  # TODO
                "z_bounds": 0  # TODO
            }

        else:
            logger.warning("Unknown printer : " + self.id)
        return properties

    def get_robot_model(self, IP):
        logger.info("Loading from ROS robot model : " + self.id)
        compas.PRECISION = '12f'
        robot, scene = None, None

        if self.id == "UR5":  # How to load different robots from here?
            if IP:
                # Load from ROS
                try:
                    with RosClient(IP) as ros:
                        # load robot class
                        robot = ros.load_robot(load_geometry=False)
                        scene = PlanningScene(robot)
                        logger.info("Loaded robot")
                except:
                    logger.warning("No connection to ROS. Have you put the correct IP and composed up docker?")

            ### Load robot from github
            from compas_fab.robots.ur5 import Robot
            robot = Robot(load_geometry=False)
            scene = PlanningScene(robot)
            print(robot.info())

        return robot, scene

    def attach_endeffector(self, FILENAME, frame):
        mesh = Mesh.from_obj(FILENAME)
        tool = Tool(mesh, frame)
        self.robot.attach_tool(tool)


if __name__ == "__main__":
    pass
