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

    def create_printpoints(self, generate_mesh_normals=True):
        """Create the print points of the fabrication process

        Parameters
        ----------
        generate_mesh_normals: bool
            Boolean toggle that controls whether to generate mesh normals or not.
            If False, mesh normals will be set to Vector(0, 0, 1)
        """

        count = 0
        logger.info('Creating print points ...')
        with progressbar.ProgressBar(max_value=self.slicer.number_of_points) as bar:

            if generate_mesh_normals:
                logger.info('Generating mesh normals ...')
                # fast method for getting the closest mesh normals to all the printpoints
                all_pts = [pt for layer in self.slicer.layers for path in layer.paths for pt in path.points]
                closest_fks, projected_pts = utils.pull_pts_to_mesh_faces(self.slicer.mesh, all_pts)
                normals = [Vector(*self.slicer.mesh.face_normal(fkey)) for fkey in closest_fks]

            for i, layer in enumerate(self.slicer.layers):
                self.printpoints_dict['layer_%d' % i] = {}

                for j, path in enumerate(layer.paths):
                    self.printpoints_dict['layer_%d' % i]['path_%d' % j] = []

                    for k, point in enumerate(path.points):

                        n = normals[count] if generate_mesh_normals else Vector(0, 1, 0)
                        printpoint = PrintPoint(pt=point, layer_height=self.slicer.layer_height, mesh_normal=n)

                        if layer.is_brim or layer.is_raft:
                            printpoint.up_vector = Vector(0, 0, 1)
                        else:
                            printpoint.up_vector = self.get_printpoint_up_vector(path, k, n)

                        self.printpoints_dict['layer_%d' % i]['path_%d' % j].append(printpoint)
                        bar.update(count)
                        count += 1


if __name__ == "__main__":
    pass
