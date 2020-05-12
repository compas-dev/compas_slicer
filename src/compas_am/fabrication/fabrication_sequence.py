import os, json
import logging
logger = logging.getLogger('logger')

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
        "robotic_printing", "3d_printer"
    """

    def __init__(self, paths_collection, machine_model, fabrication_type):
        self.paths_collection = paths_collection
        self.machine_model = machine_model
        self.type = fabrication_type

        self.visualization_geometry = None

        self.ordered_print_points = self.get_print_points_ordered_in_fabrication_sequence()
        self.commands = []

        if self.type == "robotic_printing":
            self.commands = self.create_robotic_commands()
        elif self.type == "3d_printer":
            self.commands = self.create_printer_commands()
        else: 
            raise NameError("Invalid fabrication type : "+ str(fabrication_type))


    def get_print_points_ordered_in_fabrication_sequence(self):
        pass

    def create_robotic_commands(self):
        pass

    def create_printer_commands(self):
        pass

    def generate_visualization_geometry(self):
        pass

    def save_commands_to_Gcode(self):
        pass

    def save_commands_to_Json(self, path, name):
        logger.info("Saving to Json: ", len(self.commands), "commands, on file: ", path + name)
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
