from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from compas_slicer.pre_processing.preprocessing_utils.compound_target import (
    blend_union_list,
    chamfer_union_list,
    stairs_union_list,
)
from compas_slicer.utilities.utils import remap_unbound

if TYPE_CHECKING:
    from compas.datastructures import Mesh

    from compas_slicer.pre_processing.preprocessing_utils.compound_target import CompoundTarget


__all__ = ["assign_interpolation_distance_to_mesh_vertices", "assign_interpolation_distance_to_mesh_vertex"]


def assign_interpolation_distance_to_mesh_vertices(
    mesh: Mesh, weight: float, target_LOW: CompoundTarget, target_HIGH: CompoundTarget | None
) -> None:
    """
    Fills in the 'get_distance' attribute of every vertex of the mesh.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    weight: float,
        The weighting of the distances from the lower and the upper target, from 0 to 1.
    target_LOW: :class: 'compas_slicer.pre_processing.CompoundTarget'
        The lower compound target.
    target_HIGH:  :class: 'compas_slicer.pre_processing.CompoundTarget'
        The upper compound target.
    """
    # Vectorized computation for all vertices at once
    distances = _compute_all_distances_vectorized(weight, target_LOW, target_HIGH)
    for vkey, d in zip(mesh.vertices(), distances):
        mesh.vertex[vkey]["scalar_field"] = float(d)


def _compute_all_distances_vectorized(
    weight: float, target_LOW: CompoundTarget, target_HIGH: CompoundTarget | None
) -> np.ndarray:
    """Compute weighted distances for all vertices at once."""
    if target_LOW and target_HIGH:
        return _get_weighted_distances_vectorized(weight, target_LOW, target_HIGH)
    elif target_LOW:
        offset = weight * target_LOW.get_max_dist()
        return target_LOW.get_all_distances() - offset
    else:
        raise ValueError("You need to provide at least one target")


def _get_weighted_distances_vectorized(
    weight: float, target_LOW: CompoundTarget, target_HIGH: CompoundTarget
) -> np.ndarray:
    """Vectorized weighted distance computation for all vertices."""
    d_low = target_LOW.get_all_distances()  # (n_vertices,)

    if target_HIGH.has_uneven_weights:
        # (n_boundaries, n_vertices)
        ds_high = target_HIGH.get_all_distances_array()

        if target_HIGH.number_of_boundaries > 1:
            weights = np.array(
                [remap_unbound(weight, 0, wmax, 0, 1) for wmax in target_HIGH.weight_max_per_cluster]
            )  # (n_boundaries,)
        else:
            weights = np.array([weight])

        # Broadcast: (n_boundaries, n_vertices)
        distances = (weights[:, None] - 1) * d_low + weights[:, None] * ds_high

        if target_HIGH.union_method == "min":
            return np.min(distances, axis=0)
        elif target_HIGH.union_method == "smooth":
            return np.array(
                [
                    blend_union_list(distances[:, i].tolist(), target_HIGH.union_params[0])
                    for i in range(distances.shape[1])
                ]
            )
        elif target_HIGH.union_method == "chamfer":
            return np.array(
                [
                    chamfer_union_list(distances[:, i].tolist(), target_HIGH.union_params[0])
                    for i in range(distances.shape[1])
                ]
            )
        elif target_HIGH.union_method == "stairs":
            return np.array(
                [
                    stairs_union_list(
                        distances[:, i].tolist(), target_HIGH.union_params[0], target_HIGH.union_params[1]
                    )
                    for i in range(distances.shape[1])
                ]
            )
    else:
        d_high = target_HIGH.get_all_distances()
        return d_low * (1 - weight) - d_high * weight


def assign_interpolation_distance_to_mesh_vertex(
    vkey: int, weight: float, target_LOW: CompoundTarget, target_HIGH: CompoundTarget | None
) -> float:
    """
    Fills in the 'get_distance' attribute for a single vertex with vkey.

    Parameters
    ----------
    vkey: int
        The vertex key.
    weight: float,
        The weighting of the distances from the lower and the upper target, from 0 to 1.
    target_LOW: :class: 'compas_slicer.pre_processing.CompoundTarget'
        The lower compound target.
    target_HIGH:  :class: 'compas_slicer.pre_processing.CompoundTarget'
        The upper compound target.
    """
    if target_LOW and target_HIGH:  # then interpolate targets
        d = get_weighted_distance(vkey, weight, target_LOW, target_HIGH)
    elif target_LOW:  # then offset target
        offset = weight * target_LOW.get_max_dist()
        d = target_LOW.get_distance(vkey) - offset
    else:
        raise ValueError("You need to provide at least one target")
    return d


def get_weighted_distance(vkey: int, weight: float, target_LOW: CompoundTarget, target_HIGH: CompoundTarget) -> float:
    """
    Computes the weighted get_distance for a single vertex with vkey.

    Parameters
    ----------
    vkey: int
        The vertex key.
    weight: float,
        The weighting of the distances from the lower and the upper target, from 0 to 1.
    target_LOW: :class: 'compas_slicer.pre_processing.CompoundTarget'
        The lower compound target.
    target_HIGH:  :class: 'compas_slicer.pre_processing.CompoundTarget'
        The upper compound target.
    """
    # --- calculation with uneven weights
    if target_HIGH.has_uneven_weights:
        d_low = target_LOW.get_distance(vkey)  # float
        ds_high = target_HIGH.get_all_distances_for_vkey(vkey)  # list of floats (# number_of_boundaries)

        if target_HIGH.number_of_boundaries > 1:
            weights_remapped = [
                remap_unbound(weight, 0, weight_max, 0, 1) for weight_max in target_HIGH.weight_max_per_cluster
            ]
            weights = weights_remapped
        else:
            weights = [weight]

        distances = [(weight - 1) * d_low + weight * d_high for d_high, weight in zip(ds_high, weights)]

        # return the distance based on the union method of the high target
        if target_HIGH.union_method == "min":
            # --- simple union
            return np.min(distances)
        elif target_HIGH.union_method == "smooth":
            # --- blend (smooth) union
            return blend_union_list(values=distances, r=target_HIGH.union_params[0])
        elif target_HIGH.union_method == "chamfer":
            # --- blend (smooth) union
            return chamfer_union_list(values=distances, r=target_HIGH.union_params[0])
        elif target_HIGH.union_method == "stairs":
            # --- stairs union
            return stairs_union_list(values=distances, r=target_HIGH.union_params[0], n=target_HIGH.union_params[1])

    # --- simple calculation (without uneven weights)
    else:
        d_low = target_LOW.get_distance(vkey)
        d_high = target_HIGH.get_distance(vkey)
        return (d_low * (1 - weight)) - (d_high * weight)


if __name__ == "__main__":
    pass
