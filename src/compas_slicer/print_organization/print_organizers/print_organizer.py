import compas_slicer
import logging
from compas_slicer.geometry import PrintPoint
from compas.geometry import Polyline
from compas_slicer.print_organization import add_safety_printpoints
from compas.geometry import norm_vector, Vector
import math
import compas_slicer.utilities as utils
from progress.bar import Bar

logger = logging.getLogger('logger')

__all__ = ['PrintOrganizer']


class PrintOrganizer(object):
    """
    Base class for organizing the printing process.
    """

    def __init__(self, slicer):
        assert isinstance(slicer, compas_slicer.slicers.BaseSlicer)  # check input
        self.slicer = slicer
        self.printpoints_dict = {}


    ###############################
    #  --- Initialization
    def create_printpoints_dict(self, mesh):
        logger.info('Creating print points ...')
        progress_bar = Bar('Print points', max=len(self.slicer.layers),
                           suffix='Layer %(index)i/%(max)i - %(percent)d%%')

        for i, layer in enumerate(self.slicer.layers):
            self.printpoints_dict['layer_%d' % i] = {}

            for j, path in enumerate(layer.paths):
                self.printpoints_dict['layer_%d' % i]['path_%d' % j] = []

                for k, point in enumerate(path.points):
                    printpoint = PrintPoint(pt=point, layer_height=self.slicer.layer_height,
                                            mesh_normal=utils.get_closest_mesh_normal(mesh, point),
                                            up_vector=Vector(0, 0, 1))

                    self.printpoints_dict['layer_%d' % i]['path_%d' % j].append(printpoint)
            progress_bar.next()
        progress_bar.finish()

    @property
    def number_of_layers(self):
        return len(self.printpoints_dict)

    def number_of_paths_on_layer(self, layer_index):
        return len(self.printpoints_dict['layer_%d' % layer_index])

    ###############################
    #  ---  printpoints data

    def generate_printpoints_dict(self):
        data = {}

        count = 0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for i, printpoint in enumerate(self.printpoints_dict[layer_key][path_key]):
                    neighboring_items = self.get_printpoint_neighboring_items(layer_key, path_key, i)

                    data[count] = {
                        #  geometry related data
                        "point": printpoint.pt.to_data(),
                        "frame": printpoint.frame.to_data(),
                        "layer_height": printpoint.layer_height,
                        "up_vector": printpoint.up_vector.to_data(),
                        "mesh_normal": printpoint.mesh_normal.to_data(),

                        #  print_organization related data
                        "velocity": printpoint.velocity,
                        "wait_time": printpoint.wait_time,
                        "blend_radius": get_radius(printpoint, neighboring_items),
                        "extruder_toggle": printpoint.extruder_toggle}

                    count += 1
        logger.info("Generated %d print points" % count)
        return data

    ##################################
    #  --- Fabrication related parameters

    def set_extruder_toggle(self, extruder_toggle):
        if not (extruder_toggle == "always_on"
                or extruder_toggle == "off_when_travel"):
            raise ValueError("Extruder toggle method doesn't exist")

        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                path_printpoints = self.printpoints_dict[layer_key][path_key]
                for i, printpoint in enumerate(path_printpoints):
                    if extruder_toggle == "always_on":  # single shell printing
                        printpoint.extruder_toggle = True
                    # elif extruder_toggle == "always_off":
                    #     printpoint.extruder_toggle = False
                    elif extruder_toggle == "off_when_travel":  # multiple contours
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

    def get_printpoint_neighboring_items(self, layer_key, path_key, i):
        neighboring_items = []
        if i > 0:
            neighboring_items.append(self.printpoints_dict[layer_key][path_key][i - 1])
        else:
            neighboring_items.append(None)
        if i < len(self.printpoints_dict[layer_key][path_key]) - 1:
            neighboring_items.append(self.printpoints_dict[layer_key][path_key][i + 1])
        else:
            neighboring_items.append(None)
        return neighboring_items

    def set_linear_velocity(self, velocity_type, v=25, per_layer_velocities=None):

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

    ##################################
    #  --- Visualization on viewer
    def visualize_on_viewer(self, viewer, visualize_polyline, visualize_printpoints):
        all_pts = []
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for printpoint in self.printpoints_dict[layer_key][path_key]:
                    all_pts.append(printpoint.pt)

        if visualize_polyline:
            polyline = Polyline(all_pts)
            viewer.add(polyline, name="Polyline", settings={'color': '#ffffff'})

        if visualize_printpoints:
            [viewer.add(pt, name="Point %d" % i) for i, pt in enumerate(all_pts)]


#############################
#  Nozzle linear velocity

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


#############################
#  Blend radius

def get_radius(printpoint, neighboring_items):
    d_fillet = 10.0
    buffer_d = 0.3
    radius = d_fillet
    if neighboring_items[0]:
        radius = min(radius,
                     norm_vector(
                         Vector.from_start_end(neighboring_items[0].pt, printpoint.pt)) * buffer_d)
    if neighboring_items[1]:
        radius = min(radius,
                     norm_vector(
                         Vector.from_start_end(neighboring_items[1].pt, printpoint.pt)) * buffer_d)

    radius = round(radius, 5)
    return radius


if __name__ == "__main__":
    pass
