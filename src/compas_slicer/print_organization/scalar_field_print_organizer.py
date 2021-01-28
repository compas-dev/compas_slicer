import logging
from compas_slicer.print_organization import BasePrintOrganizer
import compas_slicer.utilities as utils
from compas_slicer.geometry import PrintPoint
import progressbar
import logging
from compas.geometry import Point
from compas_slicer.pre_processing.curved_slicing_preprocessing import topological_sorting as topo_sort
from compas_slicer.print_organization.curved_print_organization import BaseBoundary
from compas_slicer.print_organization.curved_print_organization import VerticalConnectivity
from compas_slicer.parameters import get_param

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

    def __repr__(self):
        return "<ScalarFieldPrintOrganizer with %i layers>" % len(self.slicer.layers)

    def create_printpoints(self):
        """ Create the print points of the fabrication process """
        count = 0
        logger.info('Creating print points ...')
        with progressbar.ProgressBar(max_value=self.slicer.total_number_of_points) as bar:

            for i, layer in enumerate(self.slicer.layers):
                self.printpoints_dict['layer_%d' % i] = {}

                for j, path in enumerate(layer.paths):
                    self.printpoints_dict['layer_%d' % i]['path_%d' % j] = []

                    for k, point in enumerate(path.points):
                        normal = utils.get_normal_of_path_on_xy_plane(k, point, path, self.slicer.mesh)

                        printpoint = PrintPoint(pt=point, layer_height=self.slicer.layer_height, mesh_normal=normal)

                        self.printpoints_dict['layer_%d' % i]['path_%d' % j].append(printpoint)
                        bar.update(count)
                        count += 1

    def check_printpoints_feasibility(self):
        """ Check the feasibility of the print points """
        # TODO
        raise NotImplementedError


if __name__ == "__main__":
    pass
