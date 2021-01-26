# import logging
# from compas_slicer.print_organization import BasePrintOrganizer
# import compas_slicer.utilities as utils
# from compas_slicer.geometry import PrintPoint
# import progressbar
#
# logger = logging.getLogger('logger')
#
# __all__ = ['ScalarFieldPrintOrganizer']
#
#
# class ScalarFieldPrintOrganizer(BasePrintOrganizer):
#     """
#     Organizing the printing process for the realization of planar contours.
#
#     Attributes
#     ----------
#     slicer: :class:`compas_slicer.slicers.PlanarSlicer`
#         An instance of the compas_slicer.slicers.PlanarSlicer.
#     """
#
#     def __init__(self, slicer):
#         BasePrintOrganizer.__init__(self, slicer)
#
#     def __repr__(self):
#         return "<ScalarFieldPrintOrganizer with %i layers>" % len(self.slicer.layers)
#
#     def create_printpoints(self, transfer_attributes=False):
#         """ Create the print points of the fabrication process """
#         count = 0
#         logger.info('Creating print points ...')
#         with progressbar.ProgressBar(max_value=self.slicer.total_number_of_points) as bar:
#
#             for i, layer in enumerate(self.slicer.layers):
#                 self.printpoints_dict['layer_%d' % i] = {}
#
#                 for j, path in enumerate(layer.paths):
#                     self.printpoints_dict['layer_%d' % i]['path_%d' % j] = []
#
#                     for k, point in enumerate(path.points):
#                         normal = utils.get_normal_of_path_on_xy_plane(k, point, path, self.slicer.mesh)
#
#                         attributes = self.transfer_attributes_to_point(point) if transfer_attributes else {}
#
#                         printpoint = PrintPoint(pt=point, layer_height=self.slicer.layer_height,
#                                                 mesh_normal=normal, attributes=attributes)
#
#                         self.printpoints_dict['layer_%d' % i]['path_%d' % j].append(printpoint)
#                         bar.update(count)
#                         count += 1
#
#     def check_printpoints_feasibility(self):
#         """ Check the feasibility of the print points """
#         # TODO
#         raise NotImplementedError


if __name__ == "__main__":
    pass
