import networkx as nx
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger('logger')
from compas.geometry import Point
from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer
from compas_slicer.slicers.slice_utilities import create_graph_from_mesh_edges, sort_graph_connected_components
import logging
from compas.geometry import intersection_segment_plane
from progress.bar import Bar

__all__ = ['ZeroCrossingContours']


class ZeroCrossingContours(object):
    def __init__(self, mesh):
        self.mesh = mesh
        self.intersected_edges = []
        self.intersection_points = {}
        self.edge_point_index_relation = {}  # dict that stores node_index and edge relationship
        self.find_intersected_edges()

        self.sorted_point_clusters = {}
        self.sorted_edge_clusters = {}
        self.closed_paths_booleans = {}
        # self.compute()

    def compute(self):
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
                if point: # Sometimes the result can be None
                    if edge not in self.intersected_edges and tuple(reversed(edge)) not in self.intersected_edges:
                        self.intersected_edges.append(edge)
                        # create [edge - point] dictionary
                        self.intersection_points[edge] = Point(point[0], point[1], point[2]),

            # create [edge - point] dictionary
            for i, e in enumerate(self.intersection_points):
                self.edge_point_index_relation[e] = i

    def edge_is_intersected(self, u, v):
        # to be implemented by the inheriting classes
        raise NotImplementedError

    def find_zero_crossing_point(self, u, v):
        # to be implemented by the inheriting classes
        raise NotImplementedError
