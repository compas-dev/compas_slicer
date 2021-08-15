import logging
from compas_slicer.print_organization import BasePrintOrganizer
import compas_slicer.utilities as utils
from compas_slicer.geometry import PrintPoint
from compas.geometry import Vector
import progressbar
import compas_slicer

logger = logging.getLogger('logger')

__all__ = ['PlanarPrintOrganizer']


class PlanarPrintOrganizer(BasePrintOrganizer):
    """
    Organizing the printing process for the realization of planar contours.

    Attributes
    ----------
    slicer: :class:`compas_slicer.slicers.PlanarSlicer`
        An instance of the compas_slicer.slicers.PlanarSlicer.
    """

    def __init__(self, slicer):
        assert isinstance(slicer, compas_slicer.slicers.PlanarSlicer), 'Please provide a PlanarSlicer'
        BasePrintOrganizer.__init__(self, slicer)

    def __repr__(self):
        return "<PlanarPrintOrganizer with %i layers>" % len(self.slicer.layers)

    def create_printpoints(self, contour_ppts_with_mesh_normals=True):
        """ Create the print points of the fabrication process """
        count = 0
        logger.info('Creating print points ...')
        with progressbar.ProgressBar(max_value=self.slicer.number_of_points) as bar:

            if contour_ppts_with_mesh_normals:
                # fast method for getting the closest mesh normals to all the printpoints coming from contour pts
                all_contour_pts = [pt for layer in self.slicer.layers for path in layer.paths for pt in
                                   path.contour.points]
                closest_fks, projected_pts = utils.pull_pts_to_mesh_faces(self.slicer.mesh, all_contour_pts)
                normals_contour_pts = [Vector(*self.slicer.mesh.face_normal(fkey)) for fkey in closest_fks]
            else:
                # default value
                normals_contour_pts = [Vector(1, 0, 0) for layer in self.slicer.layers for path in layer.paths for pt in
                                       path.contour.points]

            for i, layer in enumerate(self.slicer.layers):
                self.printpoints_dict['layer_%d' % i] = {}

                for j, path in enumerate(layer.paths):
                    self.printpoints_dict['layer_%d' % i]['path_%d' % j] = {
                        'travel_to_contour': [],
                        'contour': [],
                        'travel_to_infill': [],
                        'infill': []
                    }

                    # --- travel to contour ppts
                    if path.travel_to_contour:
                        for k, point in enumerate(path.travel_to_contour.points):
                            n = Vector(1, 0, 0)  # default value
                            printpoint = PrintPoint(i, j, point, self.slicer.layer_height, n, 'travel_to_contour')
                            self.printpoints_dict['layer_%d' % i]['path_%d' % j]['travel_to_contour'].append(printpoint)
                            bar.update(count)
                            count += 1

                    # --- contour ppts
                    for k, point in enumerate(path.contour.points):
                        n = normals_contour_pts[count]
                        printpoint = PrintPoint(i, j, point, self.slicer.layer_height, n,
                                                path_type='contour')
                        self.printpoints_dict['layer_%d' % i]['path_%d' % j]['contour'].append(printpoint)
                        bar.update(count)
                        count += 1

                    # --- travel_to_infill ppts
                    if path.travel_to_infill:
                        for k, point in enumerate(path.travel_to_infill.points):
                            n = Vector(1, 0, 0)  # default value
                            printpoint = PrintPoint(i, j, point, self.slicer.layer_height, n, 'travel_to_infill')
                            self.printpoints_dict['layer_%d' % i]['path_%d' % j]['travel_to_infill'].append(printpoint)
                            bar.update(count)
                            count += 1

                    # --- infill paths ppts
                    if path.infill:
                        for k, point in enumerate(path.infill.points):
                            n = Vector(1, 0, 0)  # default value
                            printpoint = PrintPoint(i, j, point, self.slicer.layer_height, n, 'infill')
                            self.printpoints_dict['layer_%d' % i]['path_%d' % j]['infill'].append(printpoint)
                            bar.update(count)
                            count += 1


if __name__ == "__main__":
    pass
