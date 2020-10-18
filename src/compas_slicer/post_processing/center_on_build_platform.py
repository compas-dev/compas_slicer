from compas.geometry import Point, Frame, Transformation
from compas.datastructures import mesh_bounding_box

import logging

logger = logging.getLogger('logger')

__all__ = ['center_mesh_on_build_platform']


def center_mesh_on_build_platform(mesh, machine_data):
    """General description.
    Parameters
    ----------
    param : type
        Explanation sentence.
    Returns
    -------
    what it returns
        Explanation sentence.
    """
    # get center point of build platform
    max_x, max_y = machine_data[0], machine_data[1]
    build_platform_center_pt = Point(max_x / 2, max_y / 2, 0)

    # get center bottom point of mesh model
    bbox = mesh_bounding_box(mesh)
    corner_pts = [bbox[0], bbox[2]]

    x = [p[0] for p in corner_pts]
    y = [p[1] for p in corner_pts]
    z = [p[2] for p in corner_pts]

    mesh_center_pt = (sum(x) / 2, sum(y) / 2, sum(z) / 2)

    # transform mesh
    mesh_frame = Frame(mesh_center_pt, (1, 0, 0), (0, 1, 0))
    build_frame = Frame(build_platform_center_pt, (1, 0, 0), (0, 1, 0))

    T = Transformation.from_frame_to_frame(mesh_frame, build_frame)
    mesh.transform(T)

    logger.info("Mesh moved to center of build platform : " + str(build_platform_center_pt))

    return mesh
