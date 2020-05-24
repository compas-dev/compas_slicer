import logging
import compas
from compas.geometry import Box
from compas.datastructures import Mesh
from compas_fab.backends import RosClient
from compas_fab.robots import PlanningScene, Tool

logger = logging.getLogger('logger')


class MachineModel(object):
    """
    Class for representing various fabrication machines (3D printers, robots etc.)
    """

    def __init__(self, id, material):
        self.id = id
        self.material = material
        self.properties = self.get_machine_properties()
        self.print_parameters = self.get_print_parameters()

    def get_machine_properties(self):
        raise NotImplementedError

    def get_print_parameters(self):
        raise NotImplementedError

    def get_machine_dimensions(self):
        return self.properties["x_bounds"], self.properties["y_bounds"], self.properties["z_bounds"]

    def get_machine_bounding_box(self):
        bbox = Box.from_corner_corner_height((0, 0, 0), (self.properties["x_bounds"], self.properties["y_bounds"], 0),
                                             self.properties["z_bounds"])
        return bbox

    def set_print_parameter(self, name, value):
        self.print_parameters[name] = value

    def set_machine_property(self, name, value):
        self.properties[name] = value

    def load_machine_properties_from_json(self):
        pass  # TODO!

    def load_print_parameters_from_json(self):
        pass  # TODO!

    def save_machine_properties_to_json(self):
        pass  # TODO!

    def save_print_parameters_to_json(self):
        pass  # TODO!

    def printout_info(self):
        print("\n---- Machine Model Info ----")
        print("ID : ", self.id)
        print("Properties : ")
        print(self.properties)
        print("Print parameters: ")
        print(self.print_parameters)
        print("")

    ##############################


#### 3D printing
##############################

class FDMPrinter(MachineModel):
    """
    Class for representing FDM 3D printers.
    """

    def __init__(self, id, material):
        MachineModel.__init__(self, id, material)

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

    def get_print_parameters(self):
        print_parameters = {}

        if self.material == "PLA":
            print_parameters = {
                "extruder_temperature": 210,  # Extrusion temperature (degr C)
                "bed_temperature": 60,  # Heated bed temperature (degr C)
                "print_speed": 50,  # Movement speed (mm/s)
                "z_hop": 0  # (mm)
            }
        elif self.material == "ABS":
            print_parameters = {
                "extruder_temperature": 230,  # Extrusion temperature (degr C)
                "bed_temperature": 100,  # Heated bed temperature (degr C)
                "print_speed": 50,  # Movement speed (mm/s)
                "z_hop": 0  # (mm)
            }
        else:
            logger.warning("Unknown material : " + self.material)

        return print_parameters


##############################
#### Robotic 3D printing
##############################

class RobotPrinter(MachineModel):
    """
    Class for representing Robotic printers
    """

    def __init__(self, id, material, IP=None):
        MachineModel.__init__(self, id, material)

        self.robot, self.scene = self.get_robot_model(IP)  # compas robot

        ## print parameters
        self.properties = self.get_machine_properties()
        self.print_parameters = {}

    def get_machine_properties(self):
        properties = {}

        if self.id == "UR5":
            properties = {
                "x_bounds": 0,
                "y_bounds": 0,
                "z_bounds": 0
            }

        else:
            logger.warning("Unknown printer : " + self.id)
        return properties

    def get_print_parameters(self):
        print_parameters = {}

        if self.material == "PLA":
            print_parameters = {
                "travel_speed": 120,
                "safe_plane_height": 10  # (mm)
            }
        return print_parameters

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