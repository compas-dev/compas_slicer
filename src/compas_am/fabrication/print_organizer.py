import json
import compas_am
import logging
from compas_am.fabrication import generate_gcode

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
        compas_am.geometry.PathCollection or any class inheriting from it
    machine_model : The hardware
        compas_am.fabrication.MachineModel or any class inheriting form it
    """

    def __init__(self, paths_collection, machine_model):
        # check input
        assert isinstance(paths_collection[0], compas_am.geometry.PathCollection)
        assert isinstance(machine_model, compas_am.fabrication.MachineModel)

        self.paths_collection = paths_collection
        self.machine_model = machine_model

        self.visualization_geometry = None

    def generate_visualization_geometry(self):
        ## TODO
        pass


class FDMPrintOrganizer(PrintOrganizer):
    """
    Creates fabrication data for FDM 3D printers.
    """

    def __init__(self, paths_collection, machine_model):
        PrintOrganizer.__init__(self, paths_collection, machine_model)

    def save_commands_to_gcode(self, FILE):
        """
        Saves gcode file with the print parameters provided in the machine_model
        Only supports constant layer height
        """
        if len(self.machine_model.print_parameters) == 0:
            raise ValueError("The machine_model provided does not have print parameters")
        generate_gcode(self.paths_collection, FILE, self.machine_model)


class RoboticPrintOrganizer(PrintOrganizer):
    """
    Creates fabrication data for robotic 3D printing.
    """

    def __init__(self, paths_collection, machine_model):
        assert isinstance(machine_model,
                          compas_am.fabrication.machine_model.RobotPrinter), "Machine Model does not represent a robot"
        PrintOrganizer.__init__(self, paths_collection, machine_model)

        self.ordered_print_points = self.get_print_points_ordered_in_fabrication_sequence()
        self.commands = self.generate_robotic_fdm_commands()

    def get_print_points_ordered_in_fabrication_sequence(self):
        return [printpoint for path in self.paths_collection for contour in path.contours for printpoint in
                contour.points]

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
