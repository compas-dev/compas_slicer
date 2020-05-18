import os, json
import logging
logger = logging.getLogger('logger')
import compas_am
from compas_am.fabrication.gcode import create_gcode_script

class Fabrication_sequence:
    """
    Creates all the commands in order for fabrication
    
    Attributes
    ----------
    sorted_paths_collection : list
        compas_am.slicing.printpath.PathCollection or any class inheriting from it
    machine_model : The hardware 
        compas_am.machine_model.MachineModel or any class inheriting form it
    type : str
        "fdm", "robotic_fdm"
    """

    def __init__(self, paths_collection, machine_model):
        #check input
        assert isinstance(paths_collection[0], compas_am.slicing.printpath.PathCollection)
        assert isinstance(machine_model, compas_am.fabrication.machine_model.MachineModel)

        self.paths_collection = paths_collection
        self.machine_model = machine_model

        self.visualization_geometry = None

        ## if robotic printing
        if isinstance(machine_model, compas_am.fabrication.machine_model.RobotPrinter):
            ordered_print_points = self.get_print_points_ordered_in_fabrication_sequence()
            self.commands = self.generate_robotic_fdm_commands()


    def get_print_points_ordered_in_fabrication_sequence(self):
        pass

    def generate_robotic_fdm_commands(self):
        pass
 
    def generate_visualization_geometry(self):
        pass

    def save_commands_to_gcode(self, FILE):
        """ 
        Saves gcode file with the print parameters provided in the machine_model
        Only supports constant layer height
        """
        if len(self.machine_model.print_parameters) == 0:
            raise ValueError("The machine_model provided does not have print parameters")
        create_gcode_script(self.paths_collection, FILE, self.machine_model)


    def save_commands_to_json(self, path, name):
        logger.info("Saving to json: ", len(self.commands), "commands, on file: ", path + name)
        # data dictionary
        data = {}
        for i, c in enumerate(self.commands):
            data[i] = c.get_fabrication_command_dict()
        # create Json file
        filename = os.path.join(path, name)
        with open(filename, 'w') as f:
            f.write(json.dumps(data, indent=3, sort_keys=True))


if __name__ == "__main__":
    pass
