from __future__ import annotations

from loguru import logger
from typing import TYPE_CHECKING, Any

import numpy as np
import progressbar

from compas_slicer.geometry import VerticalLayersManager
from compas_slicer.parameters import get_param
from compas_slicer.slicers import BaseSlicer
from compas_slicer.slicers.slice_utilities import UVContours

if TYPE_CHECKING:
    from compas.datastructures import Mesh


__all__ = ['UVSlicer']


class UVSlicer(BaseSlicer):
    """Generates contours on the mesh corresponding to straight lines on the UV plane.

    Uses a UV map (from 3D space to plane) defined on mesh vertices.

    Attributes
    ----------
    mesh : Mesh
        Input mesh, must be triangular (no quads or n-gons allowed).
        Topology matters; irregular tessellation can lead to undesired results.
        Recommend: re-topologize, triangulate, and weld mesh in advance.
    vkey_to_uv : dict[int, tuple[float, float]]
        Mapping from vertex key to UV coordinates. UV should be in [0,1].
    no_of_isocurves : int
        Number of levels to generate.
    parameters : dict[str, Any]
        Slicing parameters dictionary.

    """

    def __init__(
        self,
        mesh: Mesh,
        vkey_to_uv: dict[int, tuple[float, float]],
        no_of_isocurves: int,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        logger.info('UVSlicer')
        BaseSlicer.__init__(self, mesh)

        self.vkey_to_uv = vkey_to_uv
        self.no_of_isocurves = no_of_isocurves
        self.parameters: dict[str, Any] = parameters if parameters else {}

        u = [self.vkey_to_uv[vkey][0] for vkey in mesh.vertices()]
        v = [self.vkey_to_uv[vkey][1] for vkey in mesh.vertices()]
        u_arr = np.array(u) * float(no_of_isocurves + 1)
        vkey_to_i = self.mesh.key_index()

        mesh.update_default_vertex_attributes({'uv': 0})
        for vkey in mesh.vertices():
            mesh.vertex_attribute(vkey, 'uv', (u_arr[vkey_to_i[vkey]], v[vkey_to_i[vkey]]))

    def generate_paths(self) -> None:
        """Generate isocontours."""
        paths_type = 'flat'  # 'spiral' # 'zigzag'
        v_left, v_right = 0.0, 1.0 - 1e-5

        max_dist = get_param(self.parameters, key='vertical_layers_max_centroid_dist', defaults_type='layers')
        vertical_layers_manager = VerticalLayersManager(max_dist)

        # create paths + layers
        with progressbar.ProgressBar(max_value=self.no_of_isocurves) as bar:
            for i in range(0, self.no_of_isocurves + 1):
                u_val = float(i)
                if i == 0:
                    u_val += 0.05  # contours are a bit tricky in the edges
                if paths_type == 'spiral':
                    u1, u2 = u_val, u_val + 1.0
                else:  # 'flat'
                    u1 = u2 = u_val

                p1 = (u1, v_left)
                p2 = (u2, v_right)

                contours = UVContours(self.mesh, p1, p2)
                contours.compute()
                contours.add_to_vertical_layers_manager(vertical_layers_manager)

                bar.update(i)  # advance progress bar

        self.layers = vertical_layers_manager.layers


if __name__ == "__main__":
    pass
