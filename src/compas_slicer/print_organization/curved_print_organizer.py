import logging
from compas.geometry import Point
from compas_slicer.print_organization import BasePrintOrganizer
from compas_slicer.pre_processing.curved_slicing_preprocessing import topological_sorting as topo_sort
import compas_slicer.utilities as utils
from compas_slicer.print_organization.curved_print_organization import BaseBoundary
from compas_slicer.print_organization.curved_print_organization import SegmentConnectivity

logger = logging.getLogger('logger')

__all__ = ['CurvedPrintOrganizer']


class CurvedPrintOrganizer(BasePrintOrganizer):
    """
    Organizing the printing process for the realization of non-planar contours.

    Attributes
    ----------
    slicer: :class:`compas_slicer.slicers.PlanarSlicer`
        An instance of the compas_slicer.slicers.PlanarSlicer.
    parameters: dict
    DATA_PATH: str
    """

    def __init__(self, slicer, parameters, DATA_PATH):
        BasePrintOrganizer.__init__(self, slicer)
        # assert isinstance(slicer.layers[0], VerticalLayer)  # curved printing only works with vertical layers
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
        self.parameters = parameters

        self.vertical_layers = slicer.vertical_layers
        self.horizontal_layers = slicer.horizontal_layers
        assert len(self.vertical_layers) + len(self.horizontal_layers) == len(slicer.layers)

        # topological sorting of vertical layers depending on their connectivity
        self.topo_sort_graph = None
        if len(self.vertical_layers) > 1:
            self.topological_sorting()
        self.selected_order = None

        self.segments = {}  # one segment per vertical layer
        self.create_segments_dict()
        self.create_base_boundaries()  # creation of one base boundary per vertical_layer
        self.create_segment_connectivity()

    def __repr__(self):
        return "<CurvedPrintOrganizer with %i segments>" % len(self.segments)

    def topological_sorting(self):
        """ When the print consists of various paths, this function initializes a class that creates
        a directed graph with all these parts, with the connectivity of each part reflecting which
        other parts it lies on, and which other parts lie on it."""
        max_layer_height = utils.get_param(self.parameters, 'max_layer_height', default_value=50)
        self.topo_sort_graph = topo_sort.SegmentsDirectedGraph(self.slicer.mesh, self.vertical_layers,
                                                               max_layer_height, DATA_PATH=self.DATA_PATH)

    def create_segments_dict(self):
        """ Initializes segments dictionary with empty segments. """
        for i, vertical_layer in enumerate(self.vertical_layers):
            self.segments[i] = {'boundary': None,
                                'path_collection': None}

    def create_base_boundaries(self):
        """ Creates one BaseBoundary per vertical_layer."""
        root_vs = utils.get_mesh_vertex_coords_with_attribute(self.slicer.mesh, 'boundary', 1)
        root_boundary = BaseBoundary(self.slicer.mesh, [Point(*v) for v in root_vs])

        if len(self.vertical_layers) > 1:
            for i, vertical_layer in enumerate(self.vertical_layers):
                parents_of_current_node = self.topo_sort_graph.get_parents_of_node(i)
                if len(parents_of_current_node) == 0:
                    boundary = root_boundary
                else:
                    boundary_pts = []
                    for parent_index in parents_of_current_node:
                        parent = self.vertical_layers[parent_index]
                        boundary_pts.extend(parent.paths[-1].points)
                    boundary = BaseBoundary(self.slicer.mesh, boundary_pts)
                self.segments[i]['boundary'] = boundary
        else:
            self.segments[0]['boundary'] = root_boundary

        # save intermediary outputs
        b_data = {}
        for i in self.segments:
            b_data[i] = self.segments[i]['boundary'].to_data()
        utils.save_to_json(b_data, self.OUTPUT_PATH, 'boundaries.json')

    def create_segment_connectivity(self):
        """ A SegmentConnectivity finds vertical relation between paths. Creates and fills in its printpoints."""
        for i, vertical_layer in enumerate(self.vertical_layers):
            logger.info('Creating connectivity of segment no %d' % i)
            path_collection = SegmentConnectivity(paths=vertical_layer.paths,
                                                  base_boundary=self.segments[i]['boundary'],
                                                  mesh=self.slicer.mesh,
                                                  parameters=self.parameters)
            path_collection.compute()
            self.segments[i]['path_collection'] = path_collection

    def create_printpoints(self):
        """
        Create the print points of the fabrication process
        Based on the directed graph, select one topological order.
        From each path collection in that order copy PrintPoints dictionary in the correct order.
        """
        if len(self.vertical_layers) > 1:  # the you need to select one topological order
            all_orders = self.topo_sort_graph.get_all_topological_orders()
            self.selected_order = all_orders[0]  # TODO: add more elaborate selection strategy
        else:
            self.selected_order = [0]  # there is only one segment, only this option

        if len(self.horizontal_layers) > 0:
            logger.warning('Attention, curved print organizer doesnt create printpoints for horizontal layers. \
                            Feature coming soon!')
            
        for i in self.selected_order:
            path_collection = self.segments[i]['path_collection']
            self.printpoints_dict['layer_%d' % i] = {}

            for j, path in enumerate(path_collection.paths):
                self.printpoints_dict['layer_%d' % i]['path_%d' % j] = \
                    [path_collection.printpoints[j][k] for k, p in enumerate(path.points)]

    def check_printpoints_feasibility(self):
        """ Checks if the get_distance to the closest support of every layer height is within the admissible limits. """
        max_layer_height = utils.get_param(self.parameters, 'max_layer_height', default_value=50)
        min_layer_height = utils.get_param(self.parameters, 'min_layer_height', default_value=0.1)

        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                ppt = self.printpoints_dict[layer_key][path_key]
                d = ppt.distance_to_support
                if d < min_layer_height or d > max_layer_height:
                    ppt.is_feasible = False


if __name__ == "__main__":
    pass
