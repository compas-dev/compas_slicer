import compas_am
from compas_am.slicing import BaseSlicer
import logging

logger = logging.getLogger('logger')

__all__ = ['PlanarSlicer']


class PlanarSlicer(BaseSlicer):
    def __init__(self, mesh, slicer_type="planar_numpy", layer_height=2.0):
        BaseSlicer.__init__(self, mesh)

        self.layer_height = layer_height
        self.slicer_type = slicer_type

    def slice_model(self, create_contours, create_infill, create_supports):
        if create_contours:
            self.generate_contours()

        if create_infill:
            self.generate_infill()

        if create_supports:
            self.generate_supports()

    def generate_contours(self):
        if self.slicer_type == "planar_numpy":
            logger.info("Planar contours compas numpy slicing")
            self.print_paths = compas_am.slicing.create_planar_contours_numpy(self.mesh, self.layer_height)

        elif self.slicer_type == "planar_meshcut":
            logger.info("Planar contours meshcut slicing")
            self.print_paths = compas_am.slicing.create_planar_contours_meshcut(self.mesh, self.layer_height)

        else:
            raise NameError("Invalid slicing type : " + self.slicer_type)

    def generate_infill(self):
        ## add infill to the already generated layers
        raise NotImplementedError

    def generate_supports(self):
        ## add supports to the already generated layers
        raise NotImplementedError