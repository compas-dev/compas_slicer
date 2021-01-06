import compas_slicer
from compas_slicer.slicers import BaseSlicer
from compas.geometry import Vector, Plane, Point
import logging

logger = logging.getLogger('logger')

__all__ = ['PlanarSlicer']


class PlanarSlicer(BaseSlicer):
    """
    Generates planar contours on a mesh.

    Attributes
    ----------
    mesh: :class:`compas.datastructures.Mesh`
        Input mesh, it must be a triangular mesh (i.e. no quads or n-gons allowed).
    slicer_type: str
        String representing which slicing method to use.
        options: 'default', 'cgal', 'meshcut'
    layer_height: float
        Distance between layers (slices).
    """
    def __init__(self, mesh, slicer_type="default", layer_height=2.0):
        BaseSlicer.__init__(self, mesh)

        self.layer_height = layer_height
        self.slicer_type = slicer_type

    def __repr__(self):
        return "<PlanarSlicer with %d layers and layer_height : %.2f mm>" % \
               (len(self.layers), self.layer_height)

    def generate_paths(self):
        """Generates the planar slicing paths."""
        z = [self.mesh.vertex_attribute(key, 'z') for key in self.mesh.vertices()]
        min_z, max_z = min(z), max(z)
        d = abs(min_z - max_z)
        no_of_layers = int(d / self.layer_height) + 1
        normal = Vector(0, 0, 1)
        planes = [Plane(Point(0, 0, min_z + i * self.layer_height), normal) for i in range(no_of_layers)]

        ################################
        # INSERTED FOR PRINTING OPT BEAM
        ################################
        planes = []
        plane_height = 0

        layer_range = 5
        h1 = 70
        h2 = 125
        h3 = 420
        h4 = 475
        h5 = 775
        h6 = 825
        mod_layer_height = 1.00

        max_layers = 900

        for i in range(1000):
            # h1
            if plane_height <= h1 - layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                plane_height += self.layer_height
            elif h1 - layer_range < plane_height < h1 + layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                print("Slicing layer ", i, "at a height of ", plane_height, "with a lh of", mod_layer_height)
                plane_height += mod_layer_height
            # h2
            elif plane_height <= h2 - layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                plane_height += self.layer_height
            elif h2 - layer_range < plane_height < h2 + layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                print("Slicing layer ", i, "at a height of ", plane_height, "with a lh of", mod_layer_height)
                plane_height += mod_layer_height
            # h3
            elif plane_height <= h3 - layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                plane_height += self.layer_height
            elif h3 - layer_range < plane_height < h3 + layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                print("Slicing layer ", i, "at a height of ", plane_height, "with a lh of", mod_layer_height)
                plane_height += mod_layer_height
            # h4
            elif plane_height <= h4 - layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                plane_height += self.layer_height
            elif h4 - layer_range < plane_height < h4 + layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                print("Slicing layer ", i, "at a height of ", plane_height, "with a lh of", mod_layer_height)
                plane_height += mod_layer_height
            # h5
            elif plane_height <= h5 - layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                plane_height += self.layer_height
            elif h5 - layer_range < plane_height < h5 + layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                print("Slicing layer ", i, "at a height of ", plane_height, "with a lh of", mod_layer_height)
                plane_height += mod_layer_height
            # h6
            elif plane_height <= h6 - layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                plane_height += self.layer_height
            elif h6 - layer_range < plane_height < h6 + layer_range:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                print("Slicing layer ", i, "at a height of ", plane_height, "with a lh of", mod_layer_height)
                plane_height += mod_layer_height

            elif i <= max_layers:
                planes.append(Plane(Point(0, 0, min_z + plane_height), normal))
                plane_height += self.layer_height
            else:
                break
        ################################
        # INSERTED FOR PRINTING OPT BEAM
        ################################

        planes.pop(0)  # remove planes that are on the print platform

        if self.slicer_type == "default":
            logger.info('')
            logger.info("Planar slicing using default function ...")
            self.layers = compas_slicer.slicers.create_planar_paths(self.mesh, planes)

        elif self.slicer_type == "meshcut":
            logger.info('')
            logger.info("Planar slicing using meshcut ...")
            self.layers = compas_slicer.slicers.create_planar_paths_meshcut(self.mesh, planes)

        elif self.slicer_type == "cgal":
            logger.info('')
            logger.info("Planar slicing using CGAL ...")
            self.layers = compas_slicer.slicers.create_planar_paths_cgal(self.mesh, planes)

        else:
            raise NameError("Invalid slicing type : " + self.slicer_type)


if __name__ == "__main__":
    pass
