import json
import compas_slicer
import logging
from compas_slicer.fabrication import generate_gcode

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
        self.commands = self.generate_robotic_fdm_commands()

    def get_print_points_ordered_in_fabrication_sequence(self):
        # TODO
        # return [printpoint for path in self.slicer.print_paths for contour in path.contours for printpoint in
        #         contour.printpoints]
        pass

    def generate_robotic_fdm_commands(self):
        a = self.ordered_print_points
        return []  # TODO

    def save_commands_to_json(self, FILENAME):
        logger.info("Saving to json: " + str(len(self.commands)) + " commands, on file: " + FILENAME)
        # data dictionary
        data = {}
        for i, c in enumerate(self.commands):
            data[i] = c.get_fabrication_command_dict()
        # create Json file
        with open(FILENAME, 'w') as f:
            f.write(json.dumps(data, indent=3, sort_keys=True))


if __name__ == "__main__":
    pass
