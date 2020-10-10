import compas_slicer
from compas_slicer.slicers import BaseSlicer
import logging
import time

logger = logging.getLogger('logger')

__all__ = ['PlanarSlicer']


class PlanarSlicer(BaseSlicer):
    def __init__(self, mesh, slicer_type="planar_compas", layer_height=2.0):
        BaseSlicer.__init__(self, mesh)

        self.layer_height = layer_height
        self.slicer_type = slicer_type

    def slice_model(self):
        start_time = time.time() # time measurement
        self.generate_paths()
        end_time = time.time()
        logger.info("Slicing operation took: %.2f seconds" % (end_time - start_time))

    def generate_paths(self):

        if self.slicer_type == "planar_compas":
            logger.info("Planar contours compas slicing")
            self.layers = compas_slicer.slicers.create_planar_paths(self.mesh, self.layer_height)

        elif self.slicer_type == "planar_numpy":
            logger.info("Planar contours compas numpy slicing")
            self.layers = compas_slicer.slicers.create_planar_paths_numpy(self.mesh, self.layer_height)

        elif self.slicer_type == "planar_meshcut":
            logger.info("Planar contours meshcut slicing")
            self.layers = compas_slicer.slicers.create_planar_paths_meshcut(self.mesh, self.layer_height)

        elif self.slicer_type == "planar_cgal":
            logger.info("Planar contours CGAL slicing")
            self.layers = compas_slicer.slicers.create_planar_paths_cgal(self.mesh, self.layer_height)

        else:
            raise NameError("Invalid slicing type : " + self.slicer_type)