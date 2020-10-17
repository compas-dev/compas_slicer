import logging
from compas.geometry import Point
from compas_slicer.print_organization.print_organizer import PrintOrganizer
from compas_slicer.geometry import VerticalLayer
from compas_slicer.print_organization.curved_print_organization import topological_sorting
import compas_slicer.utilities as utils
from compas_slicer.print_organization.curved_print_organization import BaseBoundary
from compas_slicer.print_organization.curved_print_organization import VerticalPathCollection
from compas_slicer.print_organization import set_extruder_toggle, set_linear_velocity

logger = logging.getLogger('logger')

__all__ = ['CurvedPrintOrganizer']


#############################################
#  RoboticPrintOrganizer
#############################################

class CurvedPrintOrganizer(PrintOrganizer):

    def __init__(self, slicer, parameters, DATA_PATH=None):
        assert isinstance(slicer.layers[0], VerticalLayer)  # curved printing only works with vertical layers
        PrintOrganizer.__init__(self, slicer)
        self.DATA_PATH = DATA_PATH
        self.parameters = parameters

        # topological sorting of vertical layers depending on their connectivity
        self.topo_sort_graph = None
        if len(self.slicer.vertical_layers) > 1:
            self.topological_sorting()

        self.segments = {}  # one segment per vertical layer
        self.create_segments_dict()
        self.base_boundaries_creation()  # creation of one base boundary per vertical_layer and segment
        self.create_vertical_path_collections()

        self.print_interruption = {}  # stores the printpoints positions where the print needs to be interrupted.

    def __repr__(self):
        return "<CurvedPrintOrganizer with %i segments>" % len(self.segments)

    def topological_sorting(self):
        self.topo_sort_graph = topological_sorting.SegmentsDirectedGraph(self.slicer.mesh, self.slicer.layers)

    def create_segments_dict(self):
        """ Initializes segments dictionary with empty segments """
        for i, vertical_layer in enumerate(self.slicer.vertical_layers):
            self.segments[i] = {'boundary': None,
                                'path_collection': None}

    def base_boundaries_creation(self):
        """ Creates one BaseBoundary per vertical_layer / segment """
        root_vs = utils.get_mesh_vertex_coords_with_attribute(self.slicer.mesh, 'boundary', 1)
        root_boundary = BaseBoundary(self.slicer.mesh, [Point(*v) for v in root_vs])

        if len(self.slicer.vertical_layers) > 1:
            for i, vertical_layer in enumerate(self.slicer.vertical_layers):
                parents_of_current_node = self.topo_sort_graph.get_parents_of_node(i)
                if len(parents_of_current_node) == 0:
                    boundary = root_boundary
                else:
                    boundary_pts = []
                    for parent_index in parents_of_current_node:
                        parent = self.slicer.vertical_layers[parent_index]
                        boundary_pts.extend(parent.paths[-1].points)
                    boundary = BaseBoundary(self.slicer.mesh, boundary_pts)
                self.segments[i]['boundary'] = boundary
        else:
            self.segments[0]['boundary'] = root_boundary

    def create_vertical_path_collections(self):
        """ A vertical_path_collection finds vertical relation between paths. Creates and fills in printpoints """
        for i, vertical_layer in enumerate(self.slicer.vertical_layers):
            logger.info('Creating VerticalPathCollection no %d' % i)
            path_collection = VerticalPathCollection(paths=vertical_layer.paths,
                                                     base_boundary=self.segments[i]['boundary'],
                                                     mesh=self.slicer.mesh,
                                                     parameters=self.parameters)
            path_collection.compute()
            self.segments[i]['path_collection'] = path_collection

    def create_printpoints(self, mesh):
        """
        Based on the topological graph, select one order.
        From each path collection in that order fill in the PrintPoints dictionary
        """
        if len(self.slicer.vertical_layers) > 1:  # the you need to select one topological order
            all_orders = self.topo_sort_graph.get_all_topological_orders()
            selected_order = all_orders[0]  # TODO: add more elaborate selection strategy
        else:
            selected_order = [0]  # there is only one segment, only this option

        for i in selected_order:
            path_collection = self.segments[i]['path_collection']
            self.printpoints_dict['layer_%d' % i] = {}

            for j, path in enumerate(path_collection.paths):
                self.printpoints_dict['layer_%d' % i]['path_%d' % j] = \
                    [path_collection.printpoints[j][k] for k, p in enumerate(path.points)]



    ############################################
    #  ---  override functions from base class

    def set_extruder_toggle(self, extruder_toggle_type=None):
        logger.info("Setting extruder toggle for vertical_layers")
        pass

    def set_linear_velocity(self, velocity_type="matching_layer_height", v=None, per_layer_velocities=None):
        logger.info("Setting linear velocity with type : " + str(velocity_type))
        set_linear_velocity(self.printpoints_dict, velocity_type, v=v, per_layer_velocities=per_layer_velocities)
