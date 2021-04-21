import logging
from compas_slicer.pre_processing.preprocessing_utils import blend_union_list, stairs_union_list, chamfer_union_list
from compas_slicer.utilities.utils import remap_unbound
import numpy as np

logger = logging.getLogger('logger')

__all__ = ['assign_interpolation_distance_to_mesh_vertices',
           'assign_interpolation_distance_to_mesh_vertex']


def assign_interpolation_distance_to_mesh_vertices(mesh, weight, target_LOW, target_HIGH):
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
    for i, vkey in enumerate(mesh.vertices()):
        d = assign_interpolation_distance_to_mesh_vertex(vkey, weight, target_LOW, target_HIGH)
        mesh.vertex[vkey]['scalar_field'] = d


def assign_interpolation_distance_to_mesh_vertex(vkey, weight, target_LOW, target_HIGH):
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
        raise ValueError('You need to provide at least one target')
    return d


def get_weighted_distance(vkey, weight, target_LOW, target_HIGH):
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
            weights_remapped = [remap_unbound(weight, 0, weight_max, 0, 1)
                                for weight_max in target_HIGH.weight_max_per_cluster]
            weights = weights_remapped
        else:
            weights = [weight]

        distances = [(weight - 1) * d_low + weight * d_high for d_high, weight in zip(ds_high, weights)]

        # return the distance based on the union method of the high target
        if target_HIGH.union_method == 'min':
            # --- simple union
            return np.min(distances)
        elif target_HIGH.union_method == 'smooth':
            # --- blend (smooth) union
            return blend_union_list(values=distances, r=target_HIGH.union_params[0])
        elif target_HIGH.union_method == 'chamfer':
            # --- blend (smooth) union
            return chamfer_union_list(values=distances, r=target_HIGH.union_params[0])
        elif target_HIGH.union_method == 'stairs':
            # --- stairs union
            return stairs_union_list(values=distances, r=target_HIGH.union_params[0], n=target_HIGH.union_params[1])

    # --- simple calculation (without uneven weights)
    else:
        d_low = target_LOW.get_distance(vkey)
        d_high = target_HIGH.get_distance(vkey)
        return (d_low * (1 - weight)) - (d_high * weight)


if __name__ == "__main__":
    pass
