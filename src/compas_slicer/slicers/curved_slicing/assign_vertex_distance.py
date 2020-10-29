import logging

logger = logging.getLogger('logger')

__all__ = ['assign_distance_to_mesh_vertices',
           'get_weighted_distance']


def assign_distance_to_mesh_vertices(mesh, weight, target_LOW, target_HIGH):
    """
    Fills in the 'distance' attribute of every vertex with the weighted average of the
    geodesic distance from the two targets.
    """
    for i, vkey in enumerate(mesh.vertices()):
        if target_LOW and target_HIGH:
            d = get_weighted_distance(vkey, weight, target_LOW, target_HIGH)
        elif target_LOW:
            offset = weight * target_LOW.max_dist
            d = target_LOW.distance(vkey) - offset
        else:
            raise ValueError('You need to provide at least one target')
        mesh.vertex[vkey]["distance"] = d


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

        distances = []
        for d_high, w in zip(ds_high, weights):
            d = (w - 1) * d_low + w * d_high
            distances.append(d)

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
