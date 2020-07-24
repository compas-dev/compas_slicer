import json
import compas_slicer
import logging
import copy

from compas_slicer.fabrication import generate_gcode
from compas_slicer.geometry import AdvancedPrintPoint

from compas.geometry import Point

logger = logging.getLogger('logger')

__all__ = ['PrintOrganizer',
           'FDMPrintOrganizer',
           'RoboticPrintOrganizer']


class PrintOrganizer(object):
    """
    Base class for organizing the printing process

    Attributes
    ----------
    paths_collection : list
        compas_slicer.geometry.PathCollection or any class inheriting from it
    machine_model : The hardware
        compas_slicer.fabrication.MachineModel or any class inheriting form it
    """

    def __init__(self, slicer, machine_model, material):
        # check input
        assert isinstance(slicer, compas_slicer.slicers.BaseSlicer)
        assert isinstance(machine_model, compas_slicer.fabrication.MachineModel)
        assert isinstance(material, compas_slicer.fabrication.Material)

        self.slicer = slicer
        self.machine_model = machine_model
        self.material = material

        self.visualization_geometry = None

    def generate_visualization_geometry(self):
        ## TODO
        pass


class FDMPrintOrganizer(PrintOrganizer):
    """
    Creates fabrication data for FDM 3D printers.
    """

    def __init__(self, slicer, machine_model, material):
        PrintOrganizer.__init__(self, slicer, machine_model, material)
        assert isinstance(slicer, compas_slicer.slicers.PlanarSlicer)

    def save_commands_to_gcode(self, FILE):
        """
        Saves gcode file with the print parameters provided in the machine_model
        Only supports constant layer height
        """
        if len(self.material.parameters) == 0:
            raise ValueError("The material provided does not have properties")
        generate_gcode(self.slicer.print_paths, self.slicer.layer_height, FILE, self.machine_model, self.material)


class RoboticPrintOrganizer(PrintOrganizer):
    """
    Creates fabrication data for robotic 3D printing.
    """

    def __init__(self, slicer, machine_model, material):
        assert isinstance(machine_model, compas_slicer.fabrication.machine_model.RobotPrinter), \
            "Machine Model does not represent a robot"
        PrintOrganizer.__init__(self, slicer, machine_model, material)

        self.ordered_print_points = self.get_print_points_ordered_in_fabrication_sequence()
        # print (self.ordered_print_points)
        self.commands = [] #self.generate_commands()

    def get_print_points_ordered_in_fabrication_sequence(self):
        # TODO
        # return [printpoint for path in self.slicer.print_paths for contour in path.contours for printpoint in
        #         contour.printpoints]
        pass

    def generate_commands(self):
        # self.commands = [printpoint for layer in self.slicer.print_paths for contour in layer.contours for printpoint in contour.printpoints.pt]
        self.commands = []
        for layer in self.slicer.print_paths:
            for contour in layer.contours:
                for printpoint in contour.printpoints:
                    self.commands.append(printpoint.pt)

    def generate_z_hop(self, z_hop=10):
        logger.info("Generating z_hop of " + str(z_hop) + " mm")
        for layer in self.slicer.print_paths:
            for i, contour in enumerate(layer.contours):
                # selects the first point in a contour (pt0)
                pt0 = contour.printpoints[0]
                # creates a (deep) copy
                pt0_copy = copy.deepcopy(pt0)
                # adds the vertical z_hop distance to the copied point
                pt0_copy.pt = Point(pt0.pt[0], pt0.pt[1], pt0.pt[2] + z_hop)
                # insert z_hop point as first point
                contour.printpoints.insert(0, pt0_copy) 
                # and append as last point
                contour.printpoints.append(pt0_copy) 

    def save_commands_to_json(self, FILENAME):
        logger.info("Saving to json: " + str(len(self.commands)) + " commands, to file: " + FILENAME)
        # data dictionary
        data = {}
        for i, cmd in enumerate(self.commands):
            data[i] = [cmd[0], cmd[1], cmd[2]]
        # create Json file
        with open(FILENAME, 'w') as f:
            f.write(json.dumps(data, indent=3, sort_keys=True))


if __name__ == "__main__":
    pass
