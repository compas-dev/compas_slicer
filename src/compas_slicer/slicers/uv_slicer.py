from compas_slicer.slicers import BaseSlicer
import logging
from compas_slicer.slicers.slice_utilities import UVContours
import numpy as np

import progressbar
from compas_slicer.geometry import VerticalLayersManager
from compas_slicer.parameters import get_param

logger = logging.getLogger('logger')

__all__ = ['UVSlicer']


class UVSlicer(BaseSlicer):
    """
    Generates the contours on the mesh that correspond to straight lines on the plane,
    using on a UV map (from 3D space to the plane) defined on the mesh vertices.

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
        Input mesh, it must be a triangular mesh (i.e. no quads or n-gons allowed)
        Note that the topology of the mesh matters, irregular tesselation can lead to undesired results.
        We recommend to 1)re-topologize, 2) triangulate, and 3) weld your mesh in advance.
    vkey_to_uv: dict {vkey : tuple (u,v)}. U,V coordinates should be in the domain [0,1]. The U coordinate
    no_of_isocurves: int, how many levels to be generated
    """

    def __init__(self, mesh, vkey_to_uv, no_of_isocurves, parameters=None):
        logger.info('UVSlicer')
        BaseSlicer.__init__(self, mesh)

        self.vkey_to_uv = vkey_to_uv
        self.no_of_isocurves = no_of_isocurves
        self.parameters = parameters if parameters else {}

        u = [self.vkey_to_uv[vkey][0] for vkey in mesh.vertices()]
        v = [self.vkey_to_uv[vkey][1] for vkey in mesh.vertices()]
        u = np.array(u) * float(no_of_isocurves + 1)
        vkey_to_i = self.mesh.key_index()

        mesh.update_default_vertex_attributes({'uv': 0})
        for vkey in mesh.vertices():
            mesh.vertex_attribute(vkey, 'uv', (u[vkey_to_i[vkey]], v[vkey_to_i[vkey]]))

    def generate_paths(self):
        """ Generates isocontours. """
        paths_type = 'flat'  # 'spiral' # 'zigzag'
        v_left, v_right = 0.0, 1.0 - 1e-5

        max_dist = get_param(self.parameters, key='vertical_layers_max_centroid_dist', defaults_type='layers')
        vertical_layers_manager = VerticalLayersManager(max_dist)

        # create paths + layers
        with progressbar.ProgressBar(max_value=self.no_of_isocurves) as bar:
            for i in range(0, self.no_of_isocurves + 1):
                if i == 0:
                    i += 0.05  # contours are a bit tricky in the edges
                if paths_type == 'spiral':
                    u1, u2 = i, i + 1.0
                else:  # 'flat'
                    u1 = u2 = i

                p1 = (u1, v_left)
                p2 = (u2, v_right)

                contours = UVContours(self.mesh, p1, p2)
                contours.compute()
                contours.add_to_vertical_layers_manager(vertical_layers_manager)

                bar.update(i)  # advance progress bar

        self.layers = vertical_layers_manager.layers


if __name__ == "__main__":
    pass
