from __future__ import annotations

from typing import TYPE_CHECKING

from compas.geometry import Frame, Point, Transformation, bounding_box
from loguru import logger

if TYPE_CHECKING:
    from compas.datastructures import Mesh


__all__ = ["move_mesh_to_point", "get_mid_pt_base", "remesh_mesh"]


def move_mesh_to_point(mesh: Mesh, target_point: Point) -> Mesh:
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

    logger.info(f"Mesh moved to: {target_point}")

    return mesh


def get_mid_pt_base(mesh: Mesh) -> Point:
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
    vertices = list(mesh.vertices_attributes("xyz"))
    bbox = bounding_box(vertices)
    corner_pts = [bbox[0], bbox[2]]

    x = [p[0] for p in corner_pts]
    y = [p[1] for p in corner_pts]
    z = [p[2] for p in corner_pts]

    mesh_mid_pt = Point((sum(x) / 2), (sum(y) / 2), (sum(z) / 2))

    return mesh_mid_pt


def remesh_mesh(mesh: Mesh, target_edge_length: float, number_of_iterations: int = 10, do_project: bool = True) -> Mesh:
    """Remesh a triangle mesh to achieve uniform edge lengths.

    Uses CGAL's isotropic remeshing to improve mesh quality for slicing.
    This can help with curved slicing and geodesic computations.

    Parameters
    ----------
    mesh : Mesh
        A compas mesh (must be triangulated).
    target_edge_length : float
        Target edge length for the remeshed output.
    number_of_iterations : int
        Number of remeshing iterations (default: 10).
    do_project : bool
        Reproject vertices onto original surface (default: True).

    Returns
    -------
    Mesh
        Remeshed compas mesh.

    Raises
    ------
    ImportError
        If compas_cgal is not available.

    Examples
    --------
    >>> from compas.datastructures import Mesh
    >>> from compas_slicer.pre_processing import remesh_mesh
    >>> mesh = Mesh.from_stl('model.stl')
    >>> remeshed = remesh_mesh(mesh, target_edge_length=2.0)
    """
    try:
        from compas_cgal.meshing import trimesh_remesh
    except ImportError as e:
        raise ImportError("remesh_mesh requires compas_cgal. Install with: pip install compas_cgal") from e

    from compas.datastructures import Mesh as CompasMesh

    M = mesh.to_vertices_and_faces()
    V, F = trimesh_remesh(M, target_edge_length, number_of_iterations, do_project)

    result = CompasMesh.from_vertices_and_faces(V.tolist(), F.tolist())

    logger.info(
        f"Remeshed: {mesh.number_of_vertices()} -> {result.number_of_vertices()} vertices, "
        f"target edge length: {target_edge_length}"
    )

    return result


if __name__ == "__main__":
    pass
