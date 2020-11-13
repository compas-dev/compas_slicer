from compas.geometry import Point
from compas_slicer.slicers.slice_utilities import create_graph_from_mesh_edges, sort_graph_connected_components
import compas_slicer.utilities as utils
import logging
from abc import abstractmethod

logger = logging.getLogger('logger')

__all__ = ['ZeroCrossingContoursBase']


class ZeroCrossingContoursBase(object):
    """
    This is meant to be extended by all classes that generate isocontours of a scalar function on a mesh.
    This class handles the two steps of iso-contouring of a triangular mesh consists of two steps;
    1)find intersected edges and 2)sort intersections using a graph to generate coherent polylines.

    The inheriting classes only have to implement the test that checks if an edge is intersected,
    and the method to find the zero crossing of an intersection.

    Attributes
    ----------
    mesh : :class: 'compas.datastructures.Mesh'

    """

    def __init__(self, mesh):
        self.mesh = mesh
        self.intersected_edges = []  # list of tupples (int, int)
        self.intersection_points = {}  # dict
        # key: tupple (int, int), The edge from which the intersection point originates.
        # value: :class: 'compas.geometry.Point', The zero-crossing point.
        self.edge_point_index_relation = {}  # dict that stores node_index and edge relationship
        # key: tupple (int, int) edge
        # value: int, index of the intersection point
        self.sorted_point_clusters = {}  # dict
        # key: int, The index of the connected component
        # value: list, :class: 'compas.geometry.Point', The sorted zero-crossing points.
        self.sorted_edge_clusters = {}  # dict
        # key: int, The index of the connected component.
        # value: list, tupple (int, int), The sorted intersected edges.
        self.closed_paths_booleans = {}  # dict
        # key: int, The index of the connected component.
        # value: bool, True if path is closed, False otherwise.

    def compute(self):
        self.find_intersected_edges()
        G = create_graph_from_mesh_edges(self.mesh, self.intersected_edges,
                                         self.intersection_points,
                                         self.edge_point_index_relation)
        self.sorted_point_clusters, self.sorted_edge_clusters = \
            sort_graph_connected_components(G, self.intersection_points)
        self.label_closed_paths()

    def label_closed_paths(self):
        for key in self.sorted_edge_clusters:
            first_edge = self.sorted_edge_clusters[key][0]
            last_edge = self.sorted_edge_clusters[key][-1]
            u, v = first_edge
            self.closed_paths_booleans[key] = u in last_edge or v in last_edge

    def find_intersected_edges(self):
        for edge in list(self.mesh.edges()):
            if self.edge_is_intersected(edge[0], edge[1]):
                point = self.find_zero_crossing_point(edge[0], edge[1])
                if point:  # Sometimes the result can be None
                    if edge not in self.intersected_edges and tuple(reversed(edge)) not in self.intersected_edges:
                        self.intersected_edges.append(edge)
                        # create [edge - point] dictionary
                        self.intersection_points[edge] = Point(point[0], point[1], point[2]),

            # create [edge - point] dictionary
            for i, e in enumerate(self.intersection_points):
                self.edge_point_index_relation[e] = i

    def save_point_clusters_as_polylines_to_json(self, DATA_PATH, name):
        all_points = {}
        for i, key in enumerate(self.sorted_point_clusters):
            all_points[i] = utils.point_list_to_dict(self.sorted_point_clusters[key])
        utils.save_to_json(all_points, DATA_PATH, name)

    # --- Abstract methods
    @abstractmethod
    def edge_is_intersected(self, u, v):
        """ Returns True if the edge u,v has a zero-crossing, False otherwise. """
        # to be implemented by the inheriting classes
        pass

    @abstractmethod
    def find_zero_crossing_point(self, u, v):
        """ Finds the position of the zero-crossing on the edge u,v. """
        # to be implemented by the inheriting classes
        pass
