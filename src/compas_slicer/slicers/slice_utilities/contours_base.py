from compas.geometry import Point, distance_point_point_sqrd
from compas.utilities.itertools import pairwise
from compas_slicer.slicers.slice_utilities import create_graph_from_mesh_edges, sort_graph_connected_components
import compas_slicer.utilities as utils
import logging
from abc import abstractmethod
from compas_slicer.geometry import Path

logger = logging.getLogger('logger')

__all__ = ['ContoursBase']


class ContoursBase(object):
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
        self.intersection_data = {}  # dict: (ui,vi) : {compas.Point}
        # key: tuple (int, int), The edge from which the intersection point originates.
        # value: :class: 'compas.geometry.Point', The zero-crossing point.
        self.edge_to_index = {}  # dict that stores node_index and edge relationship
        # key: tuple (int, int) edge
        # value: int, index of the intersection point
        self.sorted_point_clusters = {}  # dict
        # key: int, The index of the connected component
        # value: list, :class: 'compas.geometry.Point', The sorted zero-crossing points.
        self.sorted_edge_clusters = {}  # dict
        # key: int, The index of the connected component.
        # value: list, tuple (int, int), The sorted intersected edges.
        self.closed_paths_booleans = {}  # dict
        # key: int, The index of the connected component.
        # value: bool, True if path is closed, False otherwise.

    def compute(self):
        self.find_intersections()
        G = create_graph_from_mesh_edges(self.mesh, self.intersection_data, self.edge_to_index)
        sorted_indices_dict = sort_graph_connected_components(G)

        nodeDict = dict(G.nodes(data=True))
        for key in sorted_indices_dict:
            sorted_indices = sorted_indices_dict[key]
            self.sorted_edge_clusters[key] = [nodeDict[node_index]['mesh_edge'] for node_index in sorted_indices]
            self.sorted_point_clusters[key] = [self.intersection_data[e] for e in self.sorted_edge_clusters[key]]

        self.label_closed_paths()

    def label_closed_paths(self):
        for key in self.sorted_edge_clusters:
            first_edge = self.sorted_edge_clusters[key][0]
            last_edge = self.sorted_edge_clusters[key][-1]
            u, v = first_edge
            self.closed_paths_booleans[key] = u in last_edge or v in last_edge

    def find_intersections(self):
        """
        Fills in the
        dict self.intersection_data: key=(ui,vi) : [xi,yi,zi],
        dict self.edge_to_index: key=(u1,v1) : point_index. """
        for edge in list(self.mesh.edges()):
            if self.edge_is_intersected(edge[0], edge[1]):
                point = self.find_zero_crossing_data(edge[0], edge[1])
                if point:  # Sometimes the result can be None
                    if edge not in self.intersection_data and tuple(reversed(edge)) not in self.intersection_data:
                        # create [edge - point] dictionary
                        self.intersection_data[edge] = {}
                        self.intersection_data[edge] = Point(point[0], point[1], point[2])

            # create [edge - point] dictionary
            for i, e in enumerate(self.intersection_data):
                self.edge_to_index[e] = i

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
    def find_zero_crossing_data(self, u, v):
        """ Finds the position of the zero-crossing on the edge u,v. """
        # to be implemented by the inheriting classes
        pass

    def add_to_vertical_layers_manager(self, vertical_layers_manager):
        for key in self.sorted_point_clusters:
            pts = self.sorted_point_clusters[key]
            if len(pts) > 3:  # discard curves that are too small
                path = Path(pts, is_closed=self.closed_paths_booleans[key])

                vertical_layers_manager.add(path)

    @property
    def is_valid(self):
        if len(self.sorted_point_clusters) > 0:
            for key in self.sorted_point_clusters:
                pts = self.sorted_point_clusters[key]
                if len(pts) > 3:
                    path_total_length = 0.0
                    for p1, p2 in pairwise(pts):
                        path_total_length += distance_point_point_sqrd(p1, p2)
                    if path_total_length > 1.0:
                        return True  # make sure there is at least one path with acceptable length
        return False
