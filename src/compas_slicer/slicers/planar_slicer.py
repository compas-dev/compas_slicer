from __future__ import annotations

from compas.datastructures import Mesh
from compas.geometry import Plane, Point, Vector
from loguru import logger

from compas_slicer.slicers.base_slicer import BaseSlicer
from compas_slicer.slicers.planar_slicing import create_planar_paths

__all__ = ["PlanarSlicer"]


class PlanarSlicer(BaseSlicer):
    """Generates planar contours on a mesh that are parallel to the xy plane.

    Attributes
    ----------
    mesh : Mesh
        Input mesh, must be triangular (no quads or n-gons allowed).
    layer_height : float
        Distance between layers (slices) in mm.
    slice_height_range : tuple[float, float] | None
        Optional tuple (z_start, z_end) to slice only part of the model.
        Values are relative to mesh minimum height.

    """

    def __init__(
        self,
        mesh: Mesh,
        layer_height: float = 2.0,
        slice_height_range: tuple[float, float] | None = None,
    ) -> None:
        logger.info("PlanarSlicer")
        BaseSlicer.__init__(self, mesh)

        self.layer_height = layer_height
        self.slice_height_range = slice_height_range

    def __repr__(self) -> str:
        return f"<PlanarSlicer with {len(self.layers)} layers and layer_height : {self.layer_height:.2f} mm>"

    def generate_paths(self) -> None:
        """Generate the planar slicing paths."""
        z = [self.mesh.vertex_attribute(key, "z") for key in self.mesh.vertices()]
        min_z, max_z = min(z), max(z)

        if self.slice_height_range:
            if min_z <= self.slice_height_range[0] <= max_z and min_z <= self.slice_height_range[1] <= max_z:
                logger.info(
                    f"Slicing mesh in range from Z = {self.slice_height_range[0]} to Z = {self.slice_height_range[1]}."
                )
                max_z = min_z + self.slice_height_range[1]
                min_z = min_z + self.slice_height_range[0]
            else:
                logger.warning("Slice height range out of bounds of geometry, slice height range not used.")

        d = abs(min_z - max_z)
        no_of_layers = int(d / self.layer_height) + 1
        normal = Vector(0, 0, 1)
        planes = [Plane(Point(0, 0, min_z + i * self.layer_height), normal) for i in range(no_of_layers)]

        logger.info("Planar slicing using CGAL ...")
        self.layers = create_planar_paths(self.mesh, planes)
