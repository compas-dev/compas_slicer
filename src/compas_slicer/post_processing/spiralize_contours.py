from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from compas.geometry import Point

import compas_slicer
from compas_slicer.utilities.utils import pull_pts_to_mesh_faces

if TYPE_CHECKING:
    from compas_slicer.slicers import PlanarSlicer

logger = logging.getLogger('logger')

__all__ = ['spiralize_contours']


def spiralize_contours(slicer: PlanarSlicer) -> None:
    """Spiralizes contours. Only works for Planar Slicer.
    Can only be used for geometries consisting out of a single closed contour (i.e. vases).

    Parameters
    ----------
    slicer: :class: 'compas_slicer.slicers.PlanarSlicer'
        An instance of the compas_slicer.slicers.PlanarSlicer class.
    """
    logger.info('Spiralizing contours')

    if not isinstance(slicer, compas_slicer.slicers.PlanarSlicer):
        logger.warning("spiralize_contours() contours only works for PlanarSlicer. Skipping function.")
        return

    if slicer.layer_height is None:
        raise ValueError("layer_height must be set before spiralizing contours")

    for j, layer in enumerate(slicer.layers):
        if len(layer.paths) == 1:
            for path in layer.paths:
                d = slicer.layer_height / (len(path.points) - 1)
                for i, _point in enumerate(path.points):
                    # add the distance to move to the z value and create new points
                    path.points[i][2] += d * i

                # project all points of path back on the mesh surface
                _, projected_pts = pull_pts_to_mesh_faces(slicer.mesh, path.points)
                path.points = [Point(*p) for p in projected_pts]

                # remove the last item to create a smooth transition to the next layer
                path.points.pop(len(path.points) - 1)

        else:
            logger.warning(
                "Spiralize contours only works for layers consisting out of a single path, contours were "
                f"not changed, spiralize contour skipped for layer {j}"
            )


if __name__ == "__main__":
    pass
