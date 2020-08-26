import json
import compas_slicer
import logging

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
                    p = AdvancedPrintPoint( pt=printpoint,
                                            layer_height=None,
                                            up_vector=None,
                                            mesh=None,
                                            extruder_toggle=None)
                    self.commands.append(p)
   
    def set_extruder_toggle(self, extruder_toggle):
        if extruder_toggle == "always_on" or extruder_toggle == "always_off":
            for layer in self.slicer.print_paths:
                for contour in layer.contours:
                    for printpoint in contour.printpoints:
                        if extruder_toggle == "always_on":
                            # set printpoint.extruder_toggle to TRUE for all points
                            printpoint.extruder_toggle = True
                        if extruder_toggle == "always_off":
                            # set printpoint.extruder_toggle to FALSE for all points
                            printpoint.extruder_toggle = False

        if extruder_toggle ==  "off_when_travel":
            for layer in self.slicer.print_paths:
                for contour in layer.contours:
                    for i, printpoint in enumerate(contour.printpoints):
                        if i == len(contour.printpoints)-1:
                            # last point
                            printpoint.extruder_toggle = False
                        else:
                            # rest of points
                            printpoint.extruder_toggle = True

        if extruder_toggle ==  "off_when_travel_zhop":
            for layer in self.slicer.print_paths:
                for contour in layer.contours:
                    for i, printpoint in enumerate(contour.printpoints):
                        if i == 0:
                            # first point
                            printpoint.extruder_toggle = False
                        if i >= len(contour.printpoints)-2:
                            # last 2 points
                            printpoint.extruder_toggle = False
                        else:
                            # rest of points
                            printpoint.extruder_toggle = True                    

    def save_commands_to_json(self, FILENAME):
        logger.info("Saving to json: " + str(len(self.commands)) + " commands, to file: " + FILENAME)
        # data dictionary
        data = {}

        count = 0
        for layer in self.slicer.print_paths:
            for contour in layer.contours:
                for printpoint in contour.printpoints:
                    data[count] = {}
                    data[count]["pt"] = printpoint.pt[0], printpoint.pt[1], printpoint.pt[2]
                    data[count]["extruder_toggle"] = printpoint.extruder_toggle
                    data[count]["layer_height"] = printpoint.layer_height
                    count += 1

        with open(FILENAME, 'w') as f:
            f.write(json.dumps(data, indent=3, sort_keys=True))

if __name__ == "__main__":
    pass
