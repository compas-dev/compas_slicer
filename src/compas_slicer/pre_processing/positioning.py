from compas.geometry import Frame, Point
from compas.geometry import Transformation
from compas.datastructures import mesh_bounding_box

import logging

logger = logging.getLogger('logger')

__all__ = ['move_mesh_to_point',
           'get_mid_pt_base']


def move_mesh_to_point(mesh, target_point):
    """Moves (translates) a mesh to a target point.

    Parameters
    ----------
    mesh: :class:`compas.datastructures.Mesh`
        A compas mesh.
    target_point: :class:`compas.geometry.Point`
        The point to move the mesh to.
    """
    mesh_center_pt = get_mid_pt_base(mesh)

    # transform mesh
    mesh_frame = Frame(mesh_center_pt, (1, 0, 0), (0, 1, 0))
    target_frame = Frame(target_point, (1, 0, 0), (0, 1, 0))

    T = Transformation.from_frame_to_frame(mesh_frame, target_frame)
    mesh.transform(T)

    logger.info("Mesh moved to: " + str(target_point))

    return mesh


def get_mid_pt_base(mesh):
    """Gets the middle point of the base (bottom) of the mesh.

    Parameters
    ----------
    mesh: :class:`compas.datastructures.Mesh`
        A compas mesh.

    Returns
    -------
    mesh_mid_pt: :class:`compas.geometry.Point`
        Middle point of the base of the mesh.

    """
    # get center bottom point of mesh model
    bbox = mesh_bounding_box(mesh)
    corner_pts = [bbox[0], bbox[2]]

    x = [p[0] for p in corner_pts]
    y = [p[1] for p in corner_pts]
    z = [p[2] for p in corner_pts]

    mesh_mid_pt = Point((sum(x) / 2), (sum(y) / 2), (sum(z) / 2))

    return mesh_mid_pt


if __name__ == "__main__":
    pass
