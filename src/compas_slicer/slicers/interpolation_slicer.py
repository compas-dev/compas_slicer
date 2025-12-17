from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import progressbar
from loguru import logger

from compas_slicer.config import InterpolationConfig
from compas_slicer.geometry import VerticalLayersManager
from compas_slicer.pre_processing.preprocessing_utils.assign_vertex_distance import (
    assign_interpolation_distance_to_mesh_vertices,
)
from compas_slicer.slicers import BaseSlicer
from compas_slicer.slicers.slice_utilities import ScalarFieldContours

if TYPE_CHECKING:
    from compas.datastructures import Mesh

    from compas_slicer.pre_processing import InterpolationSlicingPreprocessor


__all__ = ["InterpolationSlicer"]


class InterpolationSlicer(BaseSlicer):
    """Generates non-planar contours that interpolate user-defined boundaries.

    Attributes
    ----------
    mesh : Mesh
        Input mesh, must be triangular (no quads or n-gons allowed).
        Topology matters; irregular tessellation can lead to undesired results.
        Recommend: re-topologize, triangulate, and weld mesh in advance.
    preprocessor : InterpolationSlicingPreprocessor | None
        Preprocessor containing compound targets.
    config : InterpolationConfig
        Interpolation configuration.
    n_multiplier : float
        Multiplier for number of isocurves.

    """

    def __init__(
        self,
        mesh: Mesh,
        preprocessor: InterpolationSlicingPreprocessor | None = None,
        config: InterpolationConfig | None = None,
    ) -> None:
        logger.info("InterpolationSlicer")
        BaseSlicer.__init__(self, mesh)

        # make sure the mesh of the preprocessor and the mesh of the slicer match
        if preprocessor and len(list(mesh.vertices())) != len(list(preprocessor.mesh.vertices())):
            raise ValueError(
                f"Mesh vertex count mismatch: slicer mesh has {len(list(mesh.vertices()))} vertices, "
                f"preprocessor mesh has {len(list(preprocessor.mesh.vertices()))} vertices"
            )

        self.config = config if config else InterpolationConfig()
        self.preprocessor = preprocessor
        self.n_multiplier: float = 1.0

    def generate_paths(self) -> None:
        """Generate curved paths."""
        if not self.preprocessor:
            raise ValueError("You need to provide a pre-processor in order to generate paths.")

        avg_layer_height = self.config.avg_layer_height
        n = find_no_of_isocurves(self.preprocessor.target_LOW, self.preprocessor.target_HIGH, avg_layer_height)
        params_list = get_interpolation_parameters_list(n)
        logger.info(f"{n} paths will be generated")

        vertical_layers_manager = VerticalLayersManager(avg_layer_height)

        # create paths + layers
        with progressbar.ProgressBar(max_value=len(params_list)) as bar:
            for i, param in enumerate(params_list):
                assign_interpolation_distance_to_mesh_vertices(
                    self.mesh, param, self.preprocessor.target_LOW, self.preprocessor.target_HIGH
                )
                contours = ScalarFieldContours(self.mesh)
                contours.compute()
                contours.add_to_vertical_layers_manager(vertical_layers_manager)

                bar.update(i)  # advance progress bar

        self.layers = vertical_layers_manager.layers


def find_no_of_isocurves(target_0: Any, target_1: Any, avg_layer_height: float = 1.1) -> int:
    """Return the number of isocurves to cover the distance from target_0 to target_1.

    Parameters
    ----------
    target_0 : CompoundTarget
        First target boundary.
    target_1 : CompoundTarget
        Second target boundary.
    avg_layer_height : float
        Average layer height in mm.

    Returns
    -------
    int
        Number of isocurves.

    """
    avg_ds0 = target_0.get_avg_distances_from_other_target(target_1)
    avg_ds1 = target_1.get_avg_distances_from_other_target(target_0)
    number_of_curves = ((avg_ds0 + avg_ds1) * 0.5) / avg_layer_height
    return max(1, int(number_of_curves))


def get_interpolation_parameters_list(number_of_curves: int) -> list[float]:
    """Return list of interpolation parameters from 0.0 to 0.997.

    Parameters
    ----------
    number_of_curves : int
        Number of curves to generate.

    Returns
    -------
    list[float]
        List of interpolation parameter values.

    """
    t_list: list[float] = []
    a = list(np.arange(number_of_curves + 1) / (number_of_curves + 1))
    a.pop(0)
    t_list.extend(a)
    t_list.append(0.997)
    return t_list


if __name__ == "__main__":
    pass
