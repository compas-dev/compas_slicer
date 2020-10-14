import logging
from compas.geometry import distance_point_point
from compas.geometry import Vector

logger = logging.getLogger('logger')

__all__ = ['seams_smooth']


def seams_smooth(slicer, smooth_distance):
    """Smoothes the seams (transition between layers)
    by removing points within a certain distance.

    Parameters
    ----------
    slicer : compas_slicer.slicers
        A compas_slicer.slicers instance
    smooth_distance : float
        Distance (in mm) to perform smoothing
    """

    logger.info("Smoothing seams with a distance of %i mm" % smooth_distance)

    for i, layer in enumerate(slicer.layers):
        if len(layer.paths) == 1:
            for path in layer.paths:
                pt0 = path.points[0]
                # only points in the first half of a path should be evaluated
                half_of_path = path.points[:int(len(path.points)/2)]
                for point in half_of_path:
                    if distance_point_point(pt0, point) < smooth_distance:
                        # remove points if within smooth_distance
                        path.points.pop(0)
                    else:
                        # create new point at a distance of the
                        # 'smooth_distance' from the first point,
                        # so that all seams are of equal length
                        vect = Vector.from_start_end(pt0, point)
                        vect.unitize()
                        new_pt = pt0 + (vect * smooth_distance)
                        path.points.insert(0, new_pt)
                        break
        else:
            logger.warning("Smooth seams only works for layers consisting out of a single path, paths were not changed, seam smoothing skipped for layer %i" % i)


if __name__ == "__main__":
    pass
