from __future__ import annotations

from typing import TYPE_CHECKING

import progressbar
from compas.geometry import Vector
from loguru import logger

import compas_slicer.utilities as utils
from compas_slicer.geometry import PrintLayer, PrintPath, PrintPoint
from compas_slicer.print_organization.base_print_organizer import BasePrintOrganizer

if TYPE_CHECKING:
    from compas_slicer.slicers import PlanarSlicer


__all__ = ['PlanarPrintOrganizer']


class PlanarPrintOrganizer(BasePrintOrganizer):
    """Organize the printing process for planar contours.

    Attributes
    ----------
    slicer : PlanarSlicer
        An instance of PlanarSlicer.

    """

    slicer: PlanarSlicer

    def __init__(self, slicer: PlanarSlicer) -> None:
        from compas_slicer.slicers import PlanarSlicer

        if not isinstance(slicer, PlanarSlicer):
            raise TypeError('Please provide a PlanarSlicer')
        BasePrintOrganizer.__init__(self, slicer)

    def __repr__(self) -> str:
        return f"<PlanarPrintOrganizer with {len(self.slicer.layers)} layers>"

    def create_printpoints(self, generate_mesh_normals: bool = True) -> None:
        """Create the print points of the fabrication process.

        Parameters
        ----------
        generate_mesh_normals : bool
            If True, compute mesh normals. If False, use Vector(0, 1, 0).

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

            for _i, layer in enumerate(self.slicer.layers):
                print_layer = PrintLayer()

                for _j, path in enumerate(layer.paths):
                    print_path = PrintPath()

                    for k, point in enumerate(path.points):

                        n = normals[count] if generate_mesh_normals else Vector(0, 1, 0)
                        layer_h = self.slicer.layer_height if self.slicer.layer_height else 2.0
                        printpoint = PrintPoint(pt=point, layer_height=layer_h, mesh_normal=n)

                        if layer.is_brim or layer.is_raft:
                            printpoint.up_vector = Vector(0, 0, 1)
                        else:
                            printpoint.up_vector = self.get_printpoint_up_vector(path, k, n)

                        print_path.printpoints.append(printpoint)
                        bar.update(count)
                        count += 1

                    print_layer.paths.append(print_path)

                self.printpoints.layers.append(print_layer)


if __name__ == "__main__":
    pass
