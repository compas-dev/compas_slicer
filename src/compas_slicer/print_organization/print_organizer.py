import compas_slicer
import logging
from compas_slicer.geometry import PrintPoint
from compas.geometry import Polyline
from compas_slicer.print_organization import add_safety_printpoints
from compas.geometry import Vector
import compas_slicer.utilities as utils
from progress.bar import Bar
from compas_slicer.print_organization import get_blend_radius, set_extruder_toggle, set_linear_velocity

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
    def create_printpoints(self, mesh):
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
    #  ---  add fabrication related information

    def set_extruder_toggle(self, extruder_toggle_type):
        logger.info("Setting extruder toggle with type : " + str(extruder_toggle_type))
        set_extruder_toggle(self.printpoints_dict, extruder_toggle_type)

    def add_safety_printpoints(self, z_hop):
        logger.info("Generating safety print points with height " + str(z_hop) + " mm")
        self.printpoints_dict = add_safety_printpoints(self.printpoints_dict, z_hop)

    def set_linear_velocity(self, velocity_type, v=25, per_layer_velocities=None):
        logger.info("Setting linear velocity with type : " + str(velocity_type))
        set_linear_velocity(self.printpoints_dict, velocity_type, v=25, per_layer_velocities=None)

    ###############################
    #  ---  output printpoints data
    def output_printpoints_dict(self):
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
                        "blend_radius": get_blend_radius(printpoint, neighboring_items),
                        "extruder_toggle_type": printpoint.extruder_toggle}

                    count += 1
        logger.info("Generated %d print points" % count)
        return data

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


if __name__ == "__main__":
    pass
