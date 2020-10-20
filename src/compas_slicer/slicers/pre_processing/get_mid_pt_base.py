from compas.datastructures import mesh_bounding_box
from compas.geometry import Point

import logging

logger = logging.getLogger('logger')

__all__ = ['get_mid_pt_base']


def get_mid_pt_base(mesh):
    # get center bottom point of mesh model
    bbox = mesh_bounding_box(mesh)
    corner_pts = [bbox[0], bbox[2]]

    x = [p[0] for p in corner_pts]
    y = [p[1] for p in corner_pts]
    z = [p[2] for p in corner_pts]

    mesh_center_pt = Point((sum(x) / 2), (sum(y) / 2), (sum(z) / 2))
    print(mesh_center_pt)

    return mesh_center_pt
