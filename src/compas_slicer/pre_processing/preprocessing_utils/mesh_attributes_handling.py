from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from compas.geometry import Point
from scipy.spatial import cKDTree

import compas_slicer.utilities as utils

if TYPE_CHECKING:
    from compas.datastructures import Mesh

__all__ = [
    "create_mesh_boundary_attributes",
    "get_existing_cut_indices",
    "get_existing_boundary_indices",
    "get_vertices_that_belong_to_cuts",
    "save_vertex_attributes",
    "restore_mesh_attributes",
    "replace_mesh_vertex_attribute",
]


def create_mesh_boundary_attributes(mesh: Mesh, low_boundary_vs: list[int], high_boundary_vs: list[int]) -> None:
    """
    Creates a default vertex attribute data['boundary']=0. Then it gives the value 1 to the vertices that belong
    to the lower boundary, and the value 2 to the vertices that belong to the higher boundary.
    """
    mesh.update_default_vertex_attributes({"boundary": 0})
    for vkey, data in mesh.vertices(data=True):
        if vkey in low_boundary_vs:
            data["boundary"] = 1
        elif vkey in high_boundary_vs:
            data["boundary"] = 2


###############################################
# --- Mesh existing attributes on vertices


def get_existing_cut_indices(mesh: Mesh) -> list[int]:
    """
    Returns
    ----------
        list, int.
        The cut indices (data['cut']>0) that exist on the mesh vertices.
    """
    cut_indices = []
    for _vkey, data in mesh.vertices(data=True):
        if data["cut"] > 0 and data["cut"] not in cut_indices:
            cut_indices.append(data["cut"])
    cut_indices = sorted(cut_indices)
    return cut_indices


def get_existing_boundary_indices(mesh: Mesh) -> list[int]:
    """
    Returns
    ----------
        list, int.
        The boundary indices (data['boundary']>0) that exist on the mesh vertices.
    """
    indices = []
    for _vkey, data in mesh.vertices(data=True):
        if data["boundary"] > 0 and data["boundary"] not in indices:
            indices.append(data["boundary"])
    boundary_indices = sorted(indices)
    return boundary_indices


def get_vertices_that_belong_to_cuts(mesh: Mesh, cut_indices: list[int]) -> dict[int, dict[int, list[float]]]:
    """
    Returns
    ----------
        dict, key: int, the index of each cut
              value: dict, the points that belong to this cut (point_list_to_dict format)
    """
    cuts_dict: dict[int, list[list[float]]] = {i: [] for i in cut_indices}

    for vkey, data in mesh.vertices(data=True):
        if data["cut"] > 0:
            cut_index = data["cut"]
            cuts_dict[cut_index].append(mesh.vertex_coordinates(vkey))

    result: dict[int, dict[int, list[float]]] = {}
    for cut_index in cuts_dict:
        result[cut_index] = utils.point_list_to_dict(cuts_dict[cut_index])

    return result


###############################################
# --- Save and restore attributes


def save_vertex_attributes(mesh: Mesh) -> dict[str, Any]:
    """
    Saves the boundary and cut attributes that are on the mesh on a dictionary.
    """
    v_attributes_dict: dict[str, Any] = {"boundary_1": [], "boundary_2": [], "cut": {}}

    cut_indices = []
    for _vkey, data in mesh.vertices(data=True):
        cut_index = data["cut"]
        if cut_index not in cut_indices:
            cut_indices.append(cut_index)
    cut_indices = sorted(cut_indices)

    for cut_index in cut_indices:
        v_attributes_dict["cut"][cut_index] = []

    for vkey, data in mesh.vertices(data=True):
        if data["boundary"] == 1:
            v_coords = mesh.vertex_coordinates(vkey)
            pt = Point(x=v_coords[0], y=v_coords[1], z=v_coords[2])
            v_attributes_dict["boundary_1"].append(pt)
        elif data["boundary"] == 2:
            v_coords = mesh.vertex_coordinates(vkey)
            pt = Point(x=v_coords[0], y=v_coords[1], z=v_coords[2])
            v_attributes_dict["boundary_2"].append(pt)
        if data["cut"] > 0:
            cut_index = data["cut"]
            v_coords = mesh.vertex_coordinates(vkey)
            pt = Point(x=v_coords[0], y=v_coords[1], z=v_coords[2])
            v_attributes_dict["cut"][cut_index].append(pt)
    return v_attributes_dict


def restore_mesh_attributes(mesh: Mesh, v_attributes_dict: dict[str, Any]) -> None:
    """
    Restores the cut and boundary attributes on the mesh vertices from the dictionary of the previously saved attributes
    """
    mesh.update_default_vertex_attributes({"boundary": 0})
    mesh.update_default_vertex_attributes({"cut": 0})

    D_THRESHOLD = 0.01

    # Build KDTree once for all queries
    vkeys = list(mesh.vertices())
    welded_mesh_vertices = np.array([mesh.vertex_coordinates(vkey) for vkey in vkeys], dtype=np.float64)
    indices_to_vkeys = dict(enumerate(vkeys))
    tree = cKDTree(welded_mesh_vertices)

    def _restore_attribute_batch(pts_list, attr_name, attr_value):
        """Restore attribute for a batch of points using KDTree."""
        if not pts_list:
            return
        query_pts = np.array([[p.x, p.y, p.z] if hasattr(p, "x") else p for p in pts_list], dtype=np.float64)
        distances, indices = tree.query(query_pts)
        for dist, idx in zip(distances, indices):
            if dist**2 < D_THRESHOLD:
                c_vkey = indices_to_vkeys[idx]
                mesh.vertex_attribute(c_vkey, attr_name, value=attr_value)

    _restore_attribute_batch(v_attributes_dict["boundary_1"], "boundary", 1)
    _restore_attribute_batch(v_attributes_dict["boundary_2"], "boundary", 2)

    for cut_index in v_attributes_dict["cut"]:
        _restore_attribute_batch(v_attributes_dict["cut"][cut_index], "cut", int(cut_index))


def replace_mesh_vertex_attribute(mesh: Mesh, old_attr: str, old_val: int, new_attr: str, new_val: int) -> None:
    """
    Replaces one vertex attribute with a new one. For all the vertices where data[old_attr]=old_val, then the
    old_val is replaced with 0, and data[new_attr]=new_val.
    """
    for vkey, data in mesh.vertices(data=True):
        if data[old_attr] == old_val:
            mesh.vertex_attribute(vkey, old_attr, 0)
            mesh.vertex_attribute(vkey, new_attr, new_val)


if __name__ == "__main__":
    pass
