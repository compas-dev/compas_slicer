import compas_slicer
from compas_slicer.slicers import BaseSlicer
from compas.geometry import Vector, Plane, Point
import logging

logger = logging.getLogger('logger')

__all__ = ['PlanarSlicer']


class PlanarSlicer(BaseSlicer):
    """
    PlanarSlicer implements generation of planar contours from a mesh.  

    Attributes
    ----------
    mesh : compas.datastructures.Mesh
        Input mesh, it must be a triangular mesh (i.e. no quads or n-gons allowed).
    slicer_type : string
        String representing which slicing method to use.
    layer_height : float
        Number representing the distance between layers (slices).
    """
    def __init__(self, mesh, slicer_type="default", layer_height=2.0):
        BaseSlicer.__init__(self, mesh)

        self.layer_height = layer_height
        self.slicer_type = slicer_type

    def __repr__(self):
        return "<PlanarSlicer with %d layers and layer_height : %.2f mm>" % \
               (len(self.layers), self.layer_height)

    def generate_paths(self):
        z = [self.mesh.vertex_attribute(key, 'z') for key in self.mesh.vertices()]
        min_z, max_z = min(z), max(z)
        d = abs(min_z - max_z)
        no_of_layers = int(d / self.layer_height) + 1
        normal = Vector(0, 0, 1)
        planes = [Plane(Point(0, 0, min_z + i * self.layer_height), normal) for i in range(no_of_layers)]
        planes.pop(0)  # remove planes that are on the print platform

        if self.slicer_type == "default":
            logger.info('')
            logger.info("Planar slicing using default function ...")
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
