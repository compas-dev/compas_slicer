import logging
from compas.geometry import normalize_vector, subtract_vectors, dot_vectors
from collections import deque

logger = logging.getLogger('logger')

__all__ = ['unify_paths_orientation']


def unify_paths_orientation(slicer):
    """
    Unifies the orientation of paths that are closed.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    """

    for i, layer in enumerate(slicer.layers):
        for j, path in enumerate(layer.paths):
            reference_points = None  # find reference points for each path, if possible
            if j > 0:
                reference_points = layer.paths[j-1].points
            elif i > 0 and j == 0:
                reference_points = slicer.layers[i - 1].paths[0].points

            if reference_points:  # then reorient current pts based on reference
                path.points = match_paths_orientations(path.points, reference_points, path.is_closed)


def match_paths_orientations(pts, reference_points, is_closed):
    """Check if new curve has same direction as prev curve, otherwise reverse.

    Parameters
    ----------
    pts: list, :class: 'compas.geometry.Point'. The list of points whose direction we are fixing.
    reference_points: list, :class: 'compas.geometry.Point'. [p1, p2] Two reference points.
    is_closed : bool, Determines if the path is closed or open
    """

    if len(pts) > 2 and len(reference_points) > 2:
        v1 = normalize_vector(subtract_vectors(pts[0], pts[2]))
        v2 = normalize_vector(subtract_vectors(reference_points[0], reference_points[2]))
    else:
        v1 = normalize_vector(subtract_vectors(pts[0], pts[1]))
        v2 = normalize_vector(subtract_vectors(reference_points[0], reference_points[1]))

    if dot_vectors(v1, v2) < 0:
        if is_closed:
            items = deque(reversed(pts))
            items.rotate(1)  # bring last point again in the front
            pts = list(items)
        else:
            pts.reverse()
    return pts


if __name__ == "__main__":
    pass
