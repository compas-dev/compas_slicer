import json
import compas_slicer
import logging

from compas_slicer.fabrication import generate_gcode
from compas_slicer.geometry import PrintPoint
import compas_slicer.utilities as utils
from compas.geometry import Polyline

logger = logging.getLogger('logger')

__all__ = ['PrintOrganizer']


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
        self.printpoints_dict = {}
        self.create_printpoints_dict()
        self.set_extruder_toggle(extruder_toggle_type)
        # logger.info('Created %d printpoints' % utils.length_of_flattened_dictionary(self.printpoints_dict))

        ### state booleans
        self.with_z_hop = False
        self.with_brim = False


    ### --- Initialization
    def create_printpoints_dict(self):
        for i, layer in enumerate(self.slicer.layers):
            self.printpoints_dict['layer_%d' % i] = {}

            for j, path in enumerate(layer.paths):
                self.printpoints_dict['layer_%d' % i]['path_%d' % j] = []

                for k, point in enumerate(path.points):
                    printpoint = PrintPoint(pt=point, layer_height=self.slicer.layer_height)

                    self.printpoints_dict['layer_%d' % i]['path_%d' % j].append(printpoint)

    def set_extruder_toggle(self, extruder_toggle):
        if not (extruder_toggle == "always_on"
                or extruder_toggle == "always_off"
                or extruder_toggle == "off_when_travel"):
            raise ValueError("Extruder toggle method doesn't exist")

        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                path_printpoints = self.printpoints_dict[layer_key][path_key]
                for i, printpoint in enumerate(path_printpoints):
                    if extruder_toggle == "always_on":
                        printpoint.extruder_toggle = True
                    elif extruder_toggle == "always_off":
                        printpoint.extruder_toggle = False
                    elif extruder_toggle == "off_when_travel":
                        if i == len(path_printpoints) - 1:
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
        generate_gcode(self.printpoints_dict, FILE, self.machine_model, self.material)

    def add_z_hop_printpoints(self, z_hop):
        self.with_z_hop = True
        logger.info("Generating z_hop of " + str(z_hop) + " mm")
        compas_slicer.fabrication.generate_z_hop(self.printpoints_dict, z_hop)

    ### --- Visualize on viewer

    def visualize_on_viewer(self, viewer, visualize_polyline, visualize_printpoints):
        all_pts = []
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for printpoint in self.printpoints_dict[layer_key][path_key]:
                    all_pts.append(printpoint.pt)

        if visualize_polyline:
            polyline = Polyline(all_pts)
            viewer.add(polyline, name="Polyline",
                       settings={'color': '#ffffff'})

        if visualize_printpoints:
            for i, pt in enumerate(all_pts):
                viewer.add(pt, name="Point %d" % i)

    ### --- To data
    def to_data(self):
        print_organizer_data = {'printpoints': {}}

        count = 0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for printpoint in self.printpoints_dict[layer_key][path_key]:
                    print_organizer_data['printpoints'][count] = printpoint.to_data()
                    count += 1

        return print_organizer_data

if __name__ == "__main__":
    pass
