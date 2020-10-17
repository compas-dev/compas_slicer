import compas_slicer
from compas_slicer.slicers import BaseSlicer
from compas.geometry import Vector, Plane, Point
import logging
import time
from compas_slicer.post_processing import seams_align, unify_paths_orientation

logger = logging.getLogger('logger')

__all__ = ['PlanarSlicer']


class PlanarSlicer(BaseSlicer):
    def __init__(self, mesh, slicer_type="planar_compas", layer_height=2.0):
        BaseSlicer.__init__(self, mesh)

        self.layer_height = layer_height
        self.slicer_type = slicer_type

    def __repr__(self):
        return "<PlanarSlicer with %d layers and layer_height : %.2f mm>" % \
               (len(self.layers), self.layer_height)

    def slice_model(self):
        start_time = time.time()  # time measurement
        self.generate_paths()
        end_time = time.time()
        logger.info('')
        logger.info("Slicing operation took: %.2f seconds" % (end_time - start_time))

        #  --- Align the seams between layers and unify orientation
        seams_align(self, align_with='x_axis')
        unify_paths_orientation(self)

        logger.info("Created %d Layers with %d total number of points"
                    % (len(self.layers), self.total_number_of_points))

    def generate_paths(self):

        z = [self.mesh.vertex_attribute(key, 'z') for key in self.mesh.vertices()]
        min_z, max_z = min(z), max(z)
        d = abs(min_z - max_z)
        no_of_layers = int(d / self.layer_height) + 1
        normal = Vector(0, 0, 1)
        planes = [Plane(Point(0, 0, min_z + i * self.layer_height), normal) for i in range(no_of_layers)]
        # planes.pop(0)  # remove planes that are on the print platform

        if self.slicer_type == "default":
            logger.info('')
            logger.info("Planar slicing using compas  ...")
            self.layers = compas_slicer.slicers.create_planar_paths(self.mesh, planes)

        elif self.slicer_type == "planar_meshcut":
            logger.info('')
            logger.info("Planar slicing using meshcut ...")
            self.layers = compas_slicer.slicers.create_planar_paths_meshcut(self.mesh, planes)

        elif self.slicer_type == "planar_cgal":
            logger.info('')
            logger.info("Planar slicing using CGAL ...")
            self.layers = compas_slicer.slicers.create_planar_paths_cgal(self.mesh, planes)

        else:
            raise NameError("Invalid slicing type : " + self.slicer_type)
