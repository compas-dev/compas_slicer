from __future__ import annotations

from loguru import logger
from typing import TYPE_CHECKING, Any

import numpy as np
import progressbar

from compas_slicer.geometry import VerticalLayersManager
from compas_slicer.parameters import get_param
from compas_slicer.slicers import BaseSlicer
from compas_slicer.slicers.slice_utilities import ScalarFieldContours

if TYPE_CHECKING:
    from collections.abc import Sequence

    from compas.datastructures import Mesh


__all__ = ['ScalarFieldSlicer']


class ScalarFieldSlicer(BaseSlicer):
    """Generates the isocontours of a scalar field defined on mesh vertices.

    Attributes
    ----------
    mesh : Mesh
        Input mesh, must be triangular (no quads or n-gons allowed).
        Topology matters; irregular tessellation can lead to undesired results.
        Recommend: re-topologize, triangulate, and weld mesh in advance.
    scalar_field : list[float]
        One float per vertex representing the scalar field.
    no_of_isocurves : int
        Number of isocontours to generate.
    parameters : dict[str, Any]
        Slicing parameters dictionary.

    """

    def __init__(
        self,
        mesh: Mesh,
        scalar_field: Sequence[float],
        no_of_isocurves: int,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        logger.info('ScalarFieldSlicer')
        BaseSlicer.__init__(self, mesh)

        self.no_of_isocurves = no_of_isocurves
        self.scalar_field: list[float] = list(np.array(scalar_field) - np.min(np.array(scalar_field)))
        self.parameters: dict[str, Any] = parameters if parameters else {}

        mesh.update_default_vertex_attributes({'scalar_field': 0})

    def generate_paths(self) -> None:
        """Generate isocontours."""
        start_domain, end_domain = min(self.scalar_field), max(self.scalar_field)
        step = (end_domain - start_domain) / (self.no_of_isocurves + 1)

        max_dist = get_param(self.parameters, key='vertical_layers_max_centroid_dist', defaults_type='layers')
        vertical_layers_manager = VerticalLayersManager(max_dist)

        # create paths + layers
        with progressbar.ProgressBar(max_value=self.no_of_isocurves) as bar:
            for i in range(0, self.no_of_isocurves + 1):
                for vkey, data in self.mesh.vertices(data=True):
                    if i == 0:
                        data['scalar_field'] = self.scalar_field[vkey] - 0.05 * step  # things can be tricky in the edge
                    else:
                        data['scalar_field'] = self.scalar_field[vkey] - i * step

                contours = ScalarFieldContours(self.mesh)
                contours.compute()
                contours.add_to_vertical_layers_manager(vertical_layers_manager)

                bar.update(i)  # advance progress bar

        self.layers = vertical_layers_manager.layers


if __name__ == "__main__":
    pass
