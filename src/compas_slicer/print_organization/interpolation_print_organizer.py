from compas_slicer.print_organization import BasePrintOrganizer
from compas_slicer.pre_processing.preprocessing_utils import topological_sorting as topo_sort
from compas_slicer.print_organization.curved_print_organization import BaseBoundary
import compas_slicer
from compas.geometry import closest_point_on_polyline, distance_point_point, Polyline, Vector, Point, subtract_vectors, dot_vectors, scale_vector
import logging
from compas_slicer.geometry import Path, PrintPoint
import compas_slicer.utilities as utils
from compas_slicer.parameters import get_param

logger = logging.getLogger('logger')

__all__ = ['InterpolationPrintOrganizer']


class InterpolationPrintOrganizer(BasePrintOrganizer):
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
        assert isinstance(slicer, compas_slicer.slicers.InterpolationSlicer), 'Please provide an InterpolationSlicer'
        BasePrintOrganizer.__init__(self, slicer)
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
        self.parameters = parameters

        self.vertical_layers = slicer.vertical_layers
        self.horizontal_layers = slicer.horizontal_layers
        assert len(self.vertical_layers) + len(self.horizontal_layers) == len(slicer.layers)

        if len(self.horizontal_layers) > 0:
            assert len(self.horizontal_layers) == 1, "Only one brim horizontal layer is currently supported."
            assert self.horizontal_layers[0].is_brim, "Only one brim horizontal layer is currently supported."
            logger.info('Slicer has one horizontal brim layer.')

        # topological sorting of vertical layers depending on their connectivity
        self.topo_sort_graph = None
        if len(self.vertical_layers) > 1:
            try:
                self.topological_sorting()
            except AssertionError:
                logger.exception("topology sorting failed\n")
                logger.critical("integrity of the output data ")
                # TODO: perhaps its better to be even more explicit and add a
                #  FAILED-timestamp.txt file?
        self.selected_order = None

        # creation of one base boundary per vertical_layer
        self.base_boundaries = self.create_base_boundaries()

    def __repr__(self):
        return "<InterpolationPrintOrganizer with %i vertical_layers>" % len(self.vertical_layers)

    def topological_sorting(self):
        """ When the print consists of various paths, this function initializes a class that creates
        a directed graph with all these parts, with the connectivity of each part reflecting which
        other parts it lies on, and which other parts lie on it."""
        avg_layer_height = get_param(self.parameters, key='avg_layer_height', defaults_type='layers')
        self.topo_sort_graph = topo_sort.SegmentsDirectedGraph(self.slicer.mesh, self.vertical_layers,
                                                               4 * avg_layer_height, DATA_PATH=self.DATA_PATH)

    def create_base_boundaries(self):
        """ Creates one BaseBoundary per vertical_layer."""
        bs = []
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
                bs.append(boundary)
        else:
            bs.append(root_boundary)

        # save intermediary outputs
        b_data = {i: b.to_data() for i, b in enumerate(bs)}
        utils.save_to_json(b_data, self.OUTPUT_PATH, 'boundaries.json')

        return bs

    def create_printpoints(self):
        """
        Create the print points of the fabrication process
        Based on the directed graph, select one topological order.
        From each path collection in that order copy PrintPoints dictionary in the correct order.
        """
        current_layer_index = 0

        # (1) --- First add the printpoints of the horizontal brim layer (first layer of print)
        self.printpoints_dict['layer_0'] = {}
        if len(self.horizontal_layers) > 0:  # first add horizontal brim layers
            paths = self.horizontal_layers[0].paths
            for j, path in enumerate(paths):
                self.printpoints_dict['layer_0']['path_%d' % j] = \
                    [PrintPoint(pt=point, layer_height=get_param(self.parameters, 'avg_layer_height', 'layers'),
                                mesh_normal=utils.get_normal_of_path_on_xy_plane(k, point, path, self.slicer.mesh))
                     for k, point in enumerate(path.points)]
            current_layer_index += 1

        # (2) --- Select order of vertical layers
        if len(self.vertical_layers) > 1:  # then you need to select one topological order

            if not self.topo_sort_graph:
                logger.error("no topology graph found, cannnot set the order of vertical layers")
                self.selected_order = [0]
            else:
                all_orders = self.topo_sort_graph.get_all_topological_orders()
                self.selected_order = all_orders[0]  # TODO: add more elaborate selection strategy
        else:
            self.selected_order = [0]  # there is only one segment, only this option

        # (3) --- Then create the printpoints of all the vertical layers in the selected order
        for index, i in enumerate(self.selected_order):
            layer = self.vertical_layers[i]
            self.printpoints_dict['layer_%d' % current_layer_index] = self.get_layer_ppts(layer, self.base_boundaries[i])
            current_layer_index += 1

    def get_layer_ppts(self, layer, base_boundary):
        """ Creates the PrintPoints of a single layer."""
        max_layer_height = get_param(self.parameters, key='max_layer_height', defaults_type='layers')
        min_layer_height = get_param(self.parameters, key='min_layer_height', defaults_type='layers')
        avg_layer_height = get_param(self.parameters, 'avg_layer_height', 'layers')

        all_pts = [pt for path in layer.paths for pt in path.points]
        closest_fks, projected_pts = utils.pull_pts_to_mesh_faces(self.slicer.mesh, all_pts)
        normals = [Vector(*self.slicer.mesh.face_normal(fkey)) for fkey in closest_fks]

        count = 0
        crv_to_check = Path(base_boundary.points, True)  # creation of fake path for the lower boundary

        layer_ppts = {}
        for i, path in enumerate(layer.paths):
            layer_ppts['path_%d' % i] = []

            for k, p in enumerate(path.points):
                cp = closest_point_on_polyline(p, Polyline(crv_to_check.points))
                d = distance_point_point(cp, p)

                normal = normals[count]
                ppt = PrintPoint(pt=p, layer_height=avg_layer_height, mesh_normal=normal)

                ppt.closest_support_pt = Point(*cp)
                ppt.distance_to_support = d
                ppt.layer_height = max(min(d, max_layer_height), min_layer_height)
                ppt.up_vector = self.get_printpoint_up_vector(path, k, normal)
                if dot_vectors(subtract_vectors(p, ppt.closest_support_pt), ppt.up_vector) < 0:
                    ppt.up_vector = Vector(*scale_vector(ppt.up_vector, -1))
                ppt.frame = ppt.get_frame()

                layer_ppts['path_%d' % i].append(ppt)
                count += 1

            crv_to_check = path

        return layer_ppts


if __name__ == "__main__":
    pass
