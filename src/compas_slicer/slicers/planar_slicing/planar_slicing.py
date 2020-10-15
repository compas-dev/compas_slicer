from compas.geometry import Point
from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer
from compas_slicer.slicers.slice_utilities import create_graph_from_mesh_edges, sort_graph_connected_components
import logging
from compas.geometry import intersection_segment_plane
from progress.bar import Bar
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

    # initializes progress_bar for measuring progress
    progress_bar = Bar('Slicing', max=len(planes), suffix='Layer %(index)i/%(max)i - %(percent)d%%')

    layers = []
    for i, plane in enumerate(planes):

        i = IntersectionCurveMeshPlane(mesh, plane)

        paths = []
        if len(i.sorted_point_clusters) > 0:
            for key in i.sorted_point_clusters:
                is_closed = i.closed_paths_booleans[key]
                path = Path(points=i.sorted_point_clusters[key], is_closed=is_closed)
                paths.append(path)

            layers.append(Layer(paths))
        # advance progress bar
        progress_bar.next()

    # finish progress bar
    progress_bar.finish()
    return layers


###################################
#  Intersection class
###################################


logger = logging.getLogger('logger')


#  --- Class
class IntersectionCurveMeshPlane(ZeroCrossingContours):
    def __init__(self, mesh, plane):
        self.plane = plane
        ZeroCrossingContours.__init__(self, mesh) # initialize from parent class

    def edge_is_intersected(self, u, v):
        a = self.mesh.vertex_attributes(u, 'xyz')
        b = self.mesh.vertex_attributes(v, 'xyz')
        z = [a[2], b[2]]  # check if the plane.z is withing the range of [a.z, b.z]
        return min(z) <= self.plane.point[2] <= max(z)

    def find_zero_crossing_point(self, u, v):
        a = self.mesh.vertex_attributes(u, 'xyz')
        b = self.mesh.vertex_attributes(v, 'xyz')
        return intersection_segment_plane((a, b), self.plane)

