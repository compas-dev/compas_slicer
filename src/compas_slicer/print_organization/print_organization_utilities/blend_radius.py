from compas.geometry import norm_vector, Vector

__all__ = ['get_blend_radius']


def get_blend_radius(printpoint, neighboring_items):
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
    d_fillet = 10.0
    buffer_d = 0.3
    radius = d_fillet
    if neighboring_items[0]:
        radius = min(radius,
                     norm_vector(
                         Vector.from_start_end(neighboring_items[0].pt, printpoint.pt)) * buffer_d)
    if neighboring_items[1]:
        radius = min(radius,
                     norm_vector(
                         Vector.from_start_end(neighboring_items[1].pt, printpoint.pt)) * buffer_d)

    radius = round(radius, 5)
    return radius
