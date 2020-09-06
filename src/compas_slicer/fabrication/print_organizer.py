import json
import compas_slicer
import logging

from compas_slicer.fabrication import generate_gcode
from compas_slicer.geometry import PrintPoint
import compas_slicer.utilities as utils
from compas.geometry import Polyline

logger = logging.getLogger('logger')

__all__ = ['PrintOrganizer',
           'RoboticPrintOrganizer']


class PrintOrganizer(object):
    """
    Base class for organizing the printing process
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
        self.printpoints = []
        self.path_collections_indices = {}
        self.create_printpoints()
        self.set_extruder_toggle(extruder_toggle_type)

        ### state booleans
        self.with_z_hop = False
        self.with_brim = False

    ### --- Initialization
    def create_printpoints(self):
        for i, path_collection in enumerate(self.slicer.path_collections):
            self.path_collections_indices[i] = {}

            for j, path in enumerate(path_collection.paths):
                self.path_collections_indices[i][j] = []

                for k, point in enumerate(path.points):
                    self.path_collections_indices[i][j].append(k)

                    printpoint = PrintPoint(pt=point,
                                            path_collection_index=i,
                                            path_index=j,
                                            point_index=k,
                                            layer_height=self.slicer.layer_height)
                    printpoint.parent_path = path
                    self.printpoints.append(printpoint)

    def set_extruder_toggle(self, extruder_toggle):
        if not (extruder_toggle == "always_on"
                or extruder_toggle == "always_off"
                or extruder_toggle == "off_when_travel"):
            raise ValueError("Extruder toggle method doesn't exist")

        for printpoint in self.printpoints:
            if extruder_toggle == "always_on":
                printpoint.extruder_toggle = True
            elif extruder_toggle == "always_off":
                printpoint.extruder_toggle = False
            elif extruder_toggle == "off_when_travel":
                if printpoint.is_last_path_printpoint(self.path_collections_indices):
                    printpoint.extruder_toggle = False
                else:
                    printpoint.extruder_toggle = True

    ### --- 3D printing functions

    def generate_gcode(self, FILE):
        """
        Saves gcode file with the print parameters provided in the machine_model
        Only supports constant layer height
        """
        assert isinstance(self.slicer, compas_slicer.slicers.PlanarSlicer)
        if len(self.material.parameters) == 0:
            raise ValueError("The material provided does not have properties")
        generate_gcode(self.printpoints, FILE, self.machine_model, self.material)

    def add_z_hop_printpoints(self, z_hop):
        self.with_z_hop = True
        logger.info("Generating z_hop of " + str(z_hop) + " mm")
        self.printpoints = compas_slicer.fabrication.generate_z_hop(self.printpoints, z_hop)

    def add_brim_printpoints(self, layer_width, number_of_brim_layers):
        self.with_brim = True
        logger.info("Generating brim with layer width: %.2f mm, consisting of %d layers" %
                    (layer_width, number_of_brim_layers))
        self.printpoints = compas_slicer.fabrication.generate_brim(self.printpoints, layer_width, number_of_brim_layers)

    ### --- Visualize on viewer

    def visualize_on_viewer(self, viewer, visualize_polyline, visualize_printpoints):
        all_pts = [printpoint.pt for printpoint in self.printpoints]

        if visualize_polyline:
            polyline = Polyline(all_pts)
            viewer.add(polyline, name="Polyline",
                       settings={'color': '#ffffff'})

        if visualize_printpoints:
            for i, pt in enumerate(all_pts):
                viewer.add(pt, name="Point %d" % i)


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
        logger.info("generating %d robotic commands: " % len(self.printpoints))
        # data dictionary
        commands = {}

        logger.error('COMMANDS GENERATION NOT IMPLEMENTED YET')

        for i, printpoint in enumerate(self.printpoints):
            commands[i] = {}
            pass

        return commands


if __name__ == "__main__":
    pass
