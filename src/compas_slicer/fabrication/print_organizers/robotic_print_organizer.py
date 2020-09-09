import json
import compas_slicer
import logging
from compas_slicer.fabrication.print_organizers.print_organizer import PrintOrganizer

logger = logging.getLogger('logger')

__all__ = ['RoboticPrintOrganizer']


#############################################
### RoboticPrintOrganizer
#############################################

class RoboticPrintOrganizer(PrintOrganizer):
    """
    Creates fabrication data for robotic 3D printing.
    """

    def __init__(self, slicer, machine_model, material, extruder_toggle_type="always_on"):
        assert isinstance(machine_model, compas_slicer.fabrication.machine_model.RobotPrinter), \
            "Machine Model does not represent a robot"
        PrintOrganizer.__init__(self, slicer, machine_model, material, extruder_toggle_type)

    def generate_robotic_commands_dict(self):
        logger.info("generating %d robotic commands: " % len(self.printpoints_dict))
        # data dictionary
        commands = {}

        logger.error('COMMANDS GENERATION NOT FULLY IMPLEMENTED YET')

        count = 0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for printpoint in self.printpoints_dict[layer_key][path_key]:
                    commands[count] = {}
                    commands[count]["pt"] = printpoint.pt[0], printpoint.pt[1], printpoint.pt[2]
                    commands[count]["extruder_toggle"] = printpoint.extruder_toggle
                    count += 1

        return commands


if __name__ == "__main__":
    pass
