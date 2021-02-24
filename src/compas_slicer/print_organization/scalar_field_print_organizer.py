from compas.geometry import Vector, normalize_vector
from compas_slicer.print_organization import BasePrintOrganizer
import compas_slicer.utilities as utils
from compas_slicer.geometry import PrintPoint
import progressbar
import logging
from compas_slicer.pre_processing import GradientEvaluation
from compas_slicer.utilities.attributes_transfer import transfer_mesh_attributes_to_printpoints
from compas_slicer.parameters import get_param
import compas_slicer

logger = logging.getLogger('logger')

__all__ = ['ScalarFieldPrintOrganizer']


class ScalarFieldPrintOrganizer(BasePrintOrganizer):
    """
    Organizing the printing process for the realization of planar contours.

    Attributes
    ----------
    slicer: :class:`compas_slicer.slicers.PlanarSlicer`
        An instance of the compas_slicer.slicers.PlanarSlicer.
    """

    def __init__(self, slicer, parameters, DATA_PATH):
        assert isinstance(slicer, compas_slicer.slicers.ScalarFieldSlicer), 'Please provide a ScalarFieldSlicer'
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

        self.g_evaluation = self.add_gradient_to_vertices()

    def __repr__(self):
        return "<ScalarFieldPrintOrganizer with %i layers>" % len(self.slicer.layers)

    def create_printpoints(self):
        """ Create the print points of the fabrication process """
        count = 0
        logger.info('Creating print points ...')
        with progressbar.ProgressBar(max_value=self.slicer.number_of_points) as bar:

            for i, layer in enumerate(self.slicer.layers):
                self.printpoints_dict['layer_%d' % i] = {}

                for j, path in enumerate(layer.paths):
                    self.printpoints_dict['layer_%d' % i]['path_%d' % j] = []

                    for k, point in enumerate(path.points):
                        normal = utils.get_normal_of_path_on_xy_plane(k, point, path, self.slicer.mesh)

                        h = get_param(self.parameters, 'avg_layer_height', defaults_type='layers')
                        printpoint = PrintPoint(pt=point, layer_height=h, mesh_normal=normal)

                        self.printpoints_dict['layer_%d' % i]['path_%d' % j].append(printpoint)
                        bar.update(count)
                        count += 1

        # transfer gradient information to printpoints
        transfer_mesh_attributes_to_printpoints(self.slicer.mesh, self.printpoints_dict)

        # add non-planar print data to printpoints
        for i, layer in enumerate(self.slicer.layers):
            layer_key = 'layer_%d' % i
            for j, path in enumerate(layer.paths):
                path_key = 'path_%d' % j
                for pp in self.printpoints_dict[layer_key][path_key]:
                    grad_norm = pp.attributes['gradient_norm']
                    grad = pp.attributes['gradient']
                    pp.distance_to_support = grad_norm
                    pp.layer_height = grad_norm
                    pp.up_vector = Vector(*normalize_vector(grad))
                    pp.frame = pp.get_frame()

    def add_gradient_to_vertices(self):
        g_evaluation = GradientEvaluation(self.slicer.mesh, self.DATA_PATH)
        g_evaluation.compute_gradient()
        g_evaluation.compute_gradient_norm()

        utils.save_to_json(g_evaluation.vertex_gradient_norm, self.OUTPUT_PATH, 'gradient_norm.json')
        utils.save_to_json(utils.point_list_to_dict(g_evaluation.vertex_gradient), self.OUTPUT_PATH, 'gradient.json')

        self.slicer.mesh.update_default_vertex_attributes({'gradient': 0.0})
        self.slicer.mesh.update_default_vertex_attributes({'gradient_norm': 0.0})
        for i, (v_key, data) in enumerate(self.slicer.mesh.vertices(data=True)):
            data['gradient'] = g_evaluation.vertex_gradient[i]
            data['gradient_norm'] = g_evaluation.vertex_gradient_norm[i]
        return g_evaluation


if __name__ == "__main__":
    pass
