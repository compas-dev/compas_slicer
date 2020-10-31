from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer
import logging
import progressbar
from compas.geometry import intersection_segment_plane
from compas_slicer.slicers.slice_utilities import ZeroCrossingContours

__all__ = ['create_planar_paths']


###################################
#  Intersection function
###################################

def create_planar_paths(mesh, planes):
    """
    Creates planar contours. Does not rely on external libraries.
    It is currently the only method that can return both OPEN and CLOSED paths.

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        The mesh to be sliced
    planes: list, compas.geometry.Plane
    """

    layers = []

    with progressbar.ProgressBar(max_value=len(planes)) as bar:
        for i, plane in enumerate(planes):

            intersection = IntersectionCurveMeshPlane(mesh, plane)
            intersection.compute()

            paths = []
            if len(intersection.sorted_point_clusters) > 0:
                for key in intersection.sorted_point_clusters:
                    is_closed = intersection.closed_paths_booleans[key]
                    path = Path(points=intersection.sorted_point_clusters[key], is_closed=is_closed)
                    paths.append(path)

                layers.append(Layer(paths))

            bar.update(i)

    return layers


###################################
#  Intersection class

logger = logging.getLogger('logger')


class IntersectionCurveMeshPlane(ZeroCrossingContours):
    def __init__(self, mesh, plane):
        self.plane = plane
        ZeroCrossingContours.__init__(self, mesh)  # initialize from parent class

    def edge_is_intersected(self, u, v):
        a = self.mesh.vertex_attributes(u, 'xyz')
        b = self.mesh.vertex_attributes(v, 'xyz')
        z = [a[2], b[2]]  # check if the plane.z is withing the range of [a.z, b.z]
        return min(z) <= self.plane.point[2] < max(z)

    def find_zero_crossing_point(self, u, v):
        a = self.mesh.vertex_attributes(u, 'xyz')
        b = self.mesh.vertex_attributes(v, 'xyz')
        return intersection_segment_plane((a, b), self.plane)


if __name__ == "__main__":
    pass
