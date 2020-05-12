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
    """

    def __init__(self, paths_collection, machine_model):
        self.paths_collection = paths_collection
        self.machine_model = machine_model
        self.ordered_fragments = self.get_fragments_ordered_in_fabrication_sequence()

        self.commands = []
        self.number_of_print_interruptions = 0


    def get_fragments_ordered_in_fabrication_sequence(self):
        pass

    def smooth_up_vectors_of_ordered_fragments(self):
        pass

    def create_commands(self):
        pass

    def add_safety_commands(self):
        pass

    def generate_visualization_geometry(self):
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


    def save_commands_to_Gcode(self):
        pass

if __name__ == "__main__":
    pass
