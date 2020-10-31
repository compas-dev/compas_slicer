import logging
from compas_slicer.pre_processing.curved_slicing_preprocessing import smooth_union_list

logger = logging.getLogger('logger')

__all__ = ['assign_distance_to_mesh_vertices',
           'assign_distance_to_mesh_vertex']


def assign_distance_to_mesh_vertices(mesh, weight, target_LOW, target_HIGH):
    """
    Fills in the 'distance' attribute of every vertex of the mesh.
    """
    for i, vkey in enumerate(mesh.vertices()):
        d = assign_distance_to_mesh_vertex(vkey, weight, target_LOW, target_HIGH)
        mesh.vertex[vkey]["distance"] = d


def assign_distance_to_mesh_vertex(vkey, weight, target_LOW, target_HIGH):
    """
    Finds the distance for a single vertex with vkey.
    """
    if target_LOW and target_HIGH:  # then interpolate targets
        d = get_weighted_distance(vkey, weight, target_LOW, target_HIGH)
    elif target_LOW:  # then offset target
        offset = weight * target_LOW.max_dist
        d = target_LOW.distance(vkey) - offset
    else:
        raise ValueError('You need to provide at least one target')
    return d


#####################################
# --- utils

def get_weighted_distance(vkey, t, target_LOW, target_HIGH):
    # calculation with uneven weights
    if target_HIGH.has_uneven_weights:
        d_low = target_LOW.distance(vkey)  # float
        ds_high = target_HIGH.all_clusters_distances(vkey)  # list of floats (# number_of_boundaries)

        if target_HIGH.number_of_boundaries > 1:
            weights_remapped = [remap_unbound(t, 0, t_end, 0, 1) for t_end in target_HIGH.t_end_per_cluster]
            weights = weights_remapped
        else:
            weights = [t]

        distances = [(t - 1) * d_low + t * d_high for d_high, t in zip(ds_high, weights)]

        if target_HIGH.has_smooth_union:
            return smooth_union_list(distances, target_HIGH.r)
        else:
            return min(distances)

    # simple calculation
    else:
        d_low = target_LOW.distance(vkey)
        d_high = target_HIGH.distance(vkey)
        return (d_low * (1 - t)) - (d_high * t)


def remap_unbound(input_val, in_from, in_to, out_from, out_to):
    out_range = out_to - out_from
    in_range = in_to - in_from
    in_val = input_val - in_from
    val = (float(in_val) / in_range) * out_range
    out_val = out_from + val
    return out_val


if __name__ == "__main__":
    pass
