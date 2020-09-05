import json
import compas_slicer
import logging

from compas_slicer.fabrication import generate_gcode
from compas_slicer.geometry import PrintPoint
import compas_slicer.utilities as utils

logger = logging.getLogger('logger')

__all__ = ['PrintOrganizer',
           'RoboticPrintOrganizer']


class PrintOrganizer(object):
    """
    Base class for organizing the printing process

    Attributes
    ----------
    slicer :
    machine_model : The hardware
        compas_slicer.fabrication.MachineModel or any class inheriting form it
    material :
    """

    def __init__(self, slicer, machine_model, material, extruder_toggle_type="always_on"):
        # check input
        assert isinstance(slicer, compas_slicer.slicers.BaseSlicer)
        assert isinstance(machine_model, compas_slicer.fabrication.MachineModel)
        assert isinstance(material, compas_slicer.fabrication.Material)

        self.slicer = slicer
        self.machine_model = machine_model
        self.material = material

        ### initialize print points
        self.printpoints_dict = {}
        self.create_printpoints_dict()
        self.set_extruder_toggle(extruder_toggle_type)

        ### state booleans
        self.with_z_hop = False
        self.with_brim = False

    ### --- Initialization
    def create_printpoints_dict(self):
        path_count = 0
        for path_collection in self.slicer.path_collections:
            for path in path_collection.paths:

                printpoints = []
                for point in path.points:
                    printpoint = PrintPoint(point, self.slicer.layer_height)
                    printpoint.parent_path = path
                    printpoints.append(printpoint)
                self.printpoints_dict[path_count] = printpoints
                path_count += 1

    def set_extruder_toggle(self, extruder_toggle):
        if not (extruder_toggle == "always_on"
                or extruder_toggle == "always_off"
                or extruder_toggle == "off_when_travel"):
            raise ValueError("Extruder toggle method doesn't exist")

        for key in self.printpoints_dict:
            for i, printpoint in enumerate(self.printpoints_dict[key]):
                if extruder_toggle == "always_on":
                    printpoint.extruder_toggle = True
                elif extruder_toggle == "always_off":
                    printpoint.extruder_toggle = False
                elif extruder_toggle == "off_when_travel":
                    if i == len(self.printpoints_dict[key]) - 1:
                        printpoint.extruder_toggle = False  # last points
                    else:
                        printpoint.extruder_toggle = True  # rest of points

    ### --- Other functions

    def generate_gcode(self, FILE):
        """
        Saves gcode file with the print parameters provided in the machine_model
        Only supports constant layer height
        """
        assert isinstance(self.slicer, compas_slicer.slicers.PlanarSlicer)
        if len(self.material.parameters) == 0:
            raise ValueError("The material provided does not have properties")
        generate_gcode(self.printpoints_dict, FILE, self.machine_model, self.material)

    def add_z_hop_printpoints(self, z_hop):
        self.with_z_hop = True
        logger.info("Generating z_hop of " + str(z_hop) + " mm")
        compas_slicer.fabrication.generate_z_hop(self.printpoints_dict, z_hop)

    def add_brim_printpoints(self, layer_width, number_of_brim_layers):
        self.with_brim = True
        logger.info("Generating brim with layer width: %.2f mm, consisting of %d layers" %
                    (layer_width, number_of_brim_layers))
        compas_slicer.fabrication.generate_brim(self.printpoints_dict, layer_width, number_of_brim_layers)


#############################################
### RoboticPrintOrganizer
#############################################

class RoboticPrintOrganizer(PrintOrganizer):
    """
    Creates fabrication data for robotic 3D printing.
    """

    def __init__(self, slicer, machine_model, material):
        assert isinstance(machine_model, compas_slicer.fabrication.machine_model.RobotPrinter), \
            "Machine Model does not represent a robot"
        PrintOrganizer.__init__(self, slicer, machine_model, material)

    def generate_robotic_commands_dict(self):
        logger.info("generating %d robotic commands: " % utils.length_of_flattened_dictionary(self.printpoints_dict))
        # data dictionary
        data = {}

        logger.error('COMMANDS GENERATION NOT IMPLEMENTED YET')
        count = 0

        for key in self.printpoints_dict:
            for i, printpoint in enumerate(self.printpoints_dict[key]):
                pass

        return data


if __name__ == "__main__":
    pass
