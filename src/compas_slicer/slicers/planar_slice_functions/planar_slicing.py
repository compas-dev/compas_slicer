from compas.geometry import Plane, Point, Vector
from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer

__all__ = ['create_planar_paths',
           'IntersectionCurveMeshPlane']

###################################
### Intersection class
###################################
import logging
import compas_slicer.utilities as utils

logger = logging.getLogger('logger')
from compas.geometry import intersection_segment_plane


class IntersectionCurveMeshPlane(object):

    def __init__(self, mesh, plane):
        self.mesh = mesh
        self.plane = plane
        self.intersections = []

        self.edge_clusters = {}
        self.sorted_edge_clusters = {}
        self.point_clusters = {}

        self.intersected_edges = []
        self.intersection_points = {}
        self.find_intersected_edges()
        self.generate_edge_clusters_method()
        self.generate_point_clusters_method()

        self.closed_paths_booleans = {}
        self.label_closed_paths()
        print('Paths are closed: ', self.closed_paths_booleans)

    def label_closed_paths(self):
        for key in self.sorted_edge_clusters:
            first_edge = self.sorted_edge_clusters[key][0]
            last_edge = self.sorted_edge_clusters[key][-1]
            u, v = first_edge
            self.closed_paths_booleans[key] = u in last_edge or v in last_edge

    def find_intersected_edges(self):
        for edge in list(self.mesh.edges()):
            a = self.mesh.vertex_attributes(edge[0], 'xyz')
            b = self.mesh.vertex_attributes(edge[1], 'xyz')
            point = intersection_segment_plane((a, b), self.plane)
            if point:
                self.intersected_edges.append(edge)
                self.intersection_points[edge] = Point(point[0], point[1], point[2])

    def generate_edge_clusters_method(self):  # fills:  self.edge_clusters, self.sorted_edge_clusters
        self.edge_clusters = {}  # empty dict
        self.create_edge_clusters()  ## fills in the self.edge_clusters
        self.sorted_edge_clusters = {}  # empty dict
        self.sort_edge_clusters()

    def generate_point_clusters_method(self):
        self.point_clusters = {}

        for cluster_key in self.sorted_edge_clusters:
            sorted_edges = self.sorted_edge_clusters[cluster_key]
            self.point_clusters[cluster_key] = []

            for e_vertices in sorted_edges:
                if e_vertices not in self.intersection_points:
                    u, v = e_vertices
                    e_vertices = (v, u)
                self.point_clusters[cluster_key].append(self.intersection_points[e_vertices])

    def create_edge_clusters(self):
        current_cluster_key = 0
        if len(self.intersected_edges) > 0:
            start_edge = self.intersected_edges[0]
            self.edge_clusters[current_cluster_key] = [start_edge]
            self.safety_count = 0
            self.fill_current_cluster_key_with_neighboring_intersected_edges(start_edge, current_cluster_key)

            while utils.total_length_of_dictionary(self.edge_clusters) < len(self.intersected_edges):
                current_cluster_key += 1
                start_edge = self.get_new_unvisited_start_edge()
                self.edge_clusters[current_cluster_key] = [start_edge]
                self.fill_current_cluster_key_with_neighboring_intersected_edges(start_edge, current_cluster_key)

        else:
            logger.warning('No intersected edges on this parameter')
            self.edge_clusters[current_cluster_key] = []

    def get_new_unvisited_start_edge(self):
        for e in self.intersected_edges:
            visited_edges = utils.flattened_list_of_dictionary(self.edge_clusters)
            if e not in visited_edges and tuple(reversed(e)) not in visited_edges:
                return e

    def fill_current_cluster_key_with_neighboring_intersected_edges(self, start_edge, current_cluster_key):
        neighboring_intersected_edges_to_check_further = []
        faces = self.mesh.edge_faces(u=start_edge[0], v=start_edge[1])
        for f in faces:
            if f:
                face_edges = self.mesh.face_halfedges(f)
                for e in face_edges:
                    if (e != start_edge and tuple(reversed(e)) != start_edge) \
                            and (e not in self.edge_clusters[current_cluster_key] and tuple(reversed(e)) not in
                                 self.edge_clusters[current_cluster_key]) \
                            and (e in self.intersected_edges or tuple(reversed(e)) in self.intersected_edges):
                        neighboring_intersected_edges_to_check_further.append(e)
                        self.edge_clusters[current_cluster_key].append(e)

        for start_edge in neighboring_intersected_edges_to_check_further:
            if self.safety_count < 500:  # safety exit
                self.safety_count += 1
                self.fill_current_cluster_key_with_neighboring_intersected_edges(start_edge, current_cluster_key)

    ####################### --- edge sorting
    def sort_edge_clusters(self):
        for cluster_key in self.edge_clusters:
            if len(self.edge_clusters[cluster_key]) > 0:
                accidental_start_edge = self.edge_clusters[cluster_key][0]
                sorted_edges = self.edge_region_growth(accidental_start_edge, cluster_key)
                real_start_edge = sorted_edges[-1]
                sorted_edges = self.edge_region_growth(real_start_edge, cluster_key)
                if len(sorted_edges) != len(self.edge_clusters[cluster_key]):
                    logger.error("Attention! Sorting of edge clusters couldn't find a path the contains all curves")
                    logger.error("Intersected edges : %d , Passed edges : %d " % (
                        len(self.edge_clusters[cluster_key]), len(sorted_edges)))
                    raise ValueError("Unable to cluster sorted edges")
                self.sorted_edge_clusters[cluster_key] = sorted_edges
            else:
                logger.warning('No intersected edges on this height')
                self.sorted_edge_clusters[cluster_key] = []

    def edge_region_growth(self, start_edge, cluster_key):
        sorted_edges = [start_edge]
        step = self.step_to_next_edge(start_edge, cluster_key, sorted_edges)
        count = 0
        while step and count < 1000:
            sorted_edges.append(step)
            step = self.step_to_next_edge(step, cluster_key, sorted_edges)
            count += 1
        return sorted_edges

    def step_to_next_edge(self, start_edge, cluster_key, sorted_edges):
        faces = self.mesh.edge_faces(u=start_edge[0], v=start_edge[1])
        for face in faces:
            if face:
                face_edges = self.mesh.face_halfedges(face)
                for e in face_edges:  # Attention, if face had 3 intersected edges it would get stuck
                    if (e in self.edge_clusters[cluster_key]
                        or tuple(reversed(e)) in self.edge_clusters[cluster_key]) \
                            and (e not in sorted_edges
                                 and tuple(reversed(e)) not in sorted_edges):
                        return e


###################################
### Intersection function
###################################

def create_planar_paths(mesh, layer_height):
    """
    Creates planar contours. Does not rely on external libraries.

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        The mesh to be sliced
    layer_height : float
        A number representing the height between cutting planes.
    """
    z_heights = [mesh.vertex_attribute(key, 'z') for key in mesh.vertices()]
    layers = []
    z = min(z_heights)
    z += layer_height * 0.5
    while z < max(z_heights):
        print('Cutting at height %.3f, %d percent done' % (
            z, int(100 * (z - min(z_heights)) / (max(z_heights) - min(z_heights)))))

        plane = Plane(Point(0, 0, z), Vector(0, 0, 1))
        i = IntersectionCurveMeshPlane(mesh, plane)

        paths = []
        if len(i.point_clusters) > 0:
            for key in i.point_clusters:
                is_closed = i.open_paths_booleans[key]
                path = Path(points=i.point_clusters[key], is_closed=is_closed)
                paths.append(path)

            layers.append(Layer(paths))
        z += layer_height

    return layers
