import json
import compas_slicer
import logging

from compas_slicer.geometry import PrintPoint
import compas_slicer.utilities as utils
from compas.geometry import Polyline
from compas_slicer.fabrication import add_safety_printpoints

logger = logging.getLogger('logger')

__all__ = ['PrintOrganizer']


class PrintOrganizer(object):
    """
    Base class for organizing the printing process.
    """

    def __init__(self, slicer, machine_model, extruder_toggle_type="always_on"):
        # check input
        assert isinstance(slicer, compas_slicer.slicers.BaseSlicer)
        assert isinstance(machine_model, compas_slicer.fabrication.MachineModel)

        self.slicer = slicer
        self.machine_model = machine_model

        ### initialize print points
        self.printpoints_dict = {}
        self.create_printpoints_dict()
        self.set_extruder_toggle(extruder_toggle_type)

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

            # set extruder toggle of last print point to false
            last_layer_key = 'layer_%d' % (len(self.slicer.layers) - 1)
            last_path_key = 'path_%d' % (len(self.slicer.layers[-1].paths) - 1)
            self.printpoints_dict[last_layer_key][last_path_key][-1].extruder_toggle = False

    def add_safety_printpoints(self, z_hop):
        logger.info("Generating safety print points with height " + str(z_hop) + " mm")
        self.printpoints_dict = add_safety_printpoints(self.printpoints_dict, z_hop)

    def set_linear_velocity(self, velocity_type, v=25,
                            per_layer_velocities=None):

        if not (velocity_type == "constant"
                or velocity_type == "per_layer"
                or velocity_type == "matching_layer_height"
                or velocity_type == "matching_overhang"):
            raise ValueError("Velocity method doesn't exist")

        for i, layer_key in enumerate(self.printpoints_dict):
            for path_key in self.printpoints_dict[layer_key]:
                path_printpoints = self.printpoints_dict[layer_key][path_key]
                for printpoint in path_printpoints:

                    if velocity_type == "constant":
                        printpoint.velocity = v

                    elif velocity_type == "per_layer":
                        assert per_layer_velocities, "You need to provide one velocity value per layer"
                        assert len(per_layer_velocities) == self.number_of_layers(), \
                            'Wrong number of velocity values. You need to provide one velocity value per layer, ' \
                            'on the "per_layer_velocities" list.'
                        printpoint.velocity = per_layer_velocities[i]

                    elif velocity_type == "matching_layer_height":
                        printpoint.velocity = calculate_linear_velocity(printpoint)

                    elif velocity_type == "matching_overhang":
                        raise NotImplementedError

    def number_of_layers(self):
        return len(self.printpoints_dict)

    def number_of_paths(self, layer_index):
        return len(self.printpoints_dict['layer_%d' % layer_index])

    ##################################
    ### --- Visualization on viewer
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

    ##################################
    ### --- To data, from data
    def to_data(self):
        print_organizer_data = {'printpoints': {}}

        count = 0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for printpoint in self.printpoints_dict[layer_key][path_key]:
                    print_organizer_data['printpoints'][count] = printpoint.to_data()
                    count += 1

        return print_organizer_data

    def from_data(cls, self):
        raise NotImplementedError


#############################
### Nozzle linear velocity
#############################
import math

motor_omega = 2 * math.pi  # 1 revolution / sec = 2*pi rad/sec
motor_r = 4.0  # 4.25 #mm
motor_linear_speed = motor_omega * motor_r
D_filament = 2.75  # mm
filament_area = math.pi * (D_filament / 2.0) ** 2  # pi*r^2

multiplier = 0.25  # arbitrary value! You might have to change this


def calculate_linear_velocity(printpoint):  # path_area * robot_linear_speed = filament_area * motor_linear_speed
    layer_width = max(printpoint.layer_height, 0.4)
    path_area = layer_width * printpoint.layer_height
    linear_speed = (filament_area * motor_linear_speed) / path_area
    return linear_speed * multiplier


if __name__ == "__main__":
    pass
