from __future__ import annotations

import copy
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

import networkx as nx
import numpy as np
from compas.datastructures import Mesh
from compas.geometry import Point
from loguru import logger

import compas_slicer.utilities as utils
from compas_slicer._numpy_ops import min_distances_to_set
from compas_slicer.pre_processing.preprocessing_utils import get_existing_boundary_indices, get_existing_cut_indices

if TYPE_CHECKING:
    from compas_slicer.geometry import VerticalLayer


__all__ = ['MeshDirectedGraph',
           'SegmentsDirectedGraph']


#################################
#  DirectedGraph

class DirectedGraph:
    """
    Base class for topological sorting of prints that consist of several parts that lie on each other.
    For example the graph A->B->C would represent a print that consists of three parts; A, B, C
    where A lies on the build platform, B lies on A, and C lies on B.
    This graph cannot have cycles; cycles would represent an unfeasible print.
    """

    def __init__(self) -> None:
        logger.info('Topological sorting')

        self.G: nx.DiGraph = nx.DiGraph()
        self.create_graph_nodes()
        self.root_indices = self.find_roots()
        logger.info('Graph roots : ' + str(self.root_indices))
        if len(self.root_indices) == 0:
            raise ValueError("No root nodes were found. At least one root node is needed.")
        self.end_indices = self.find_ends()
        logger.info('Graph ends : ' + str(self.end_indices))
        if len(self.end_indices) == 0:
            raise ValueError("No end nodes were found. At least one end node is needed.")

        self.create_directed_graph_edges(copy.deepcopy(self.root_indices))
        logger.info('Nodes : ' + str(self.G.nodes(data=True)))
        logger.info('Edges : ' + str(self.G.edges(data=True)))

        self.N: int = len(list(self.G.nodes()))
        self.adj_list: list[list[int]] = self.get_adjacency_list()  # Nested list where adj_list[i] is a list of all the neighbors
        # of the i-th component
        self.check_that_all_nodes_found_their_connectivity()
        logger.info('Adjacency list : ' + str(self.adj_list))
        self.in_degree: list[int] = self.get_in_degree()  # Nested list where adj_list[i] is a list of all the edges pointing
        # to the i-th node.
        self.all_orders: list[list[int]] = []

    def __repr__(self) -> str:
        return f"<DirectedGraph with {len(list(self.G.nodes()))} nodes>"

    # ------------------------------------ Methods to be implemented by inheriting classes
    @abstractmethod
    def find_roots(self) -> list[int]:
        """ Roots are vertical_layers_print_data that lie on the build platform. Like that they can be print first. """
        pass

    @abstractmethod
    def find_ends(self) -> list[int]:
        """ Ends are vertical_layers_print_data that belong to exclusively one segment. Like that they can be print last. """
        pass

    @abstractmethod
    def create_graph_nodes(self) -> None:
        """ Add the nodes to the graph with their attributes. """
        pass

    @abstractmethod
    def get_children_of_node(self, root: int) -> tuple[list[int], list[Any]]:
        """ Find all the vertical_layers_print_data that lie on the current root segment. """
        pass

    # ------------------------------------ Creation of graph connectivity between different nodes
    def create_directed_graph_edges(self, root_indices: list[int]) -> None:
        """ Create the connectivity of the directed graph using breadth-first search graph traversal. """
        passed_nodes = []
        queue = root_indices

        while len(queue) > 0:
            queue = self.sort_queue_with_end_targets_last(queue)
            current_node = queue[0]
            queue.remove(current_node)
            passed_nodes.append(current_node)
            children, cut_ids = self.get_children_of_node(current_node)
            for child_key, common_cuts in zip(children, cut_ids):
                self.G.add_edge(current_node, child_key, cut=common_cuts)
            for child_key in children:
                assert child_key not in passed_nodes, 'Error, cyclic directed graph.'
            for child_key in children:
                if child_key not in queue:
                    queue.append(child_key)

    def check_that_all_nodes_found_their_connectivity(self) -> None:
        """ Assert that there is no island, i.e. no node or groups of nodes that are not connected to the base. """
        good_nodes = list(self.root_indices)
        for children_list in self.adj_list:
            for child in children_list:
                if child not in good_nodes:
                    good_nodes.append(child)
        assert len(good_nodes) == self.N, 'There are floating vertical_layers_print_data on directed graph. Investigate the process of \
                                          the creation of the graph. '

    def sort_queue_with_end_targets_last(self, queue: list[int]) -> list[int]:
        """ Sorts the queue so that the vertical_layers_print_data that have an end target are always at the end. """
        queue_copy = copy.deepcopy(queue)
        for index in queue:
            if index in self.end_indices:
                queue_copy.remove(index)  # remove it from its current position
                queue_copy.append(index)  # append it last
        return queue_copy

    # ------------------------------------ Find all topological orders
    def get_adjacency_list(self) -> list[list[int]]:
        """ Returns adjacency list. Nested list where adj_list[i] is a list of all the neighbors of the ith component"""
        adj_list: list[list[int]] = [[] for _ in range(self.N)]  # adjacency list , size = len(Nodes), stores nodes' neighbors
        for i, adjacent_to_node in self.G.adjacency():
            for key in adjacent_to_node:
                adj_list[i].append(key)
        return adj_list

    def get_in_degree(self) -> list[int]:
        """ Returns in_degree list. Nested list where adj_list[i] is a list of all the edges pointing to the node."""
        in_degree = [0] * self.N  # in_degree,  size = len(Nodes) , stores in-degree of a node
        for key_degree_tuple in self.G.in_degree:
            key = key_degree_tuple[0]
            degree = key_degree_tuple[1]
            in_degree[key] = degree
        return in_degree

    def get_all_topological_orders(self) -> list[list[int]]:
        """
        Finds  all topological orders from source to sink.
        Returns
        ----------
        list of lists of integers. Each list represents the indices of one topological order.
        """
        self.all_orders = []  # make sure list is empty
        discovered = [False] * self.N
        path: list[int] = []  # list to store the topological order
        self.get_orders(path, discovered)
        logger.info(f'Found {len(self.all_orders)} possible orders')
        return self.all_orders

    def get_orders(self, path: list[int], discovered: list[bool]) -> None:
        """
        Finds all topological orders from source to sink.
        Sorting algorithm taken from https://www.techiedelight.com/find-all-possible-topological-orderings-of-dag/
        """
        for v in range(self.N):  # for every node
            # proceed only if in-degree of current node is 0 and current node is not processed yet
            if self.in_degree[v] == 0 and not discovered[v]:

                # for every adjacent vertex u of v, reduce in-degree of u by 1
                for u in self.adj_list[v]:
                    self.in_degree[u] = self.in_degree[u] - 1

                # include current node in the path and mark it as discovered
                path.append(v)
                discovered[v] = True

                # recur
                self.get_orders(path, discovered)

                # backtrack: reset in-degree information for the current node
                for u in self.adj_list[v]:
                    self.in_degree[u] = self.in_degree[u] + 1

                # backtrack: remove current node from the path and mark it as undiscovered
                path.pop()
                discovered[v] = False

        # print the topological order if all vertices are included in the path
        if len(path) == self.N:
            self.all_orders.append(copy.deepcopy(path))

    def get_parents_of_node(self, node_index: int) -> list[int]:
        """ Returns the parents of node with i = node_index. """
        return [j for j, adj in enumerate(self.adj_list) if node_index in adj]


#################################
#  --- Meshes DirectedGraph


class MeshDirectedGraph(DirectedGraph):
    """ The MeshDirectedGraph is used for topological sorting of multiple meshes that have been
    generated as a result of region split over the saddle points of the mesh scalar function """

    def __init__(self, all_meshes: list[Mesh], DATA_PATH: str) -> None:
        self.all_meshes = all_meshes
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
        DirectedGraph.__init__(self)

    def find_roots(self) -> list[int]:
        """ Roots are vertical_layers_print_data that lie on the build platform. Like that they can be print first. """
        roots: list[int] = []
        for i, mesh in enumerate(self.all_meshes):
            for _vkey, data in mesh.vertices(data=True):
                if i not in roots and data['boundary'] == 1:
                    roots.append(i)
        return roots

    def find_ends(self) -> list[int]:
        """ Ends are vertical_layers_print_data that belong to exclusively one segment. Like that they can be print last. """
        ends: list[int] = []
        for i, mesh in enumerate(self.all_meshes):
            for _vkey, data in mesh.vertices(data=True):
                if i not in ends and data['boundary'] == 2:
                    ends.append(i)
        return ends

    def create_graph_nodes(self) -> None:
        """ Add each of the split meshes to the graph as nodes. Cuts and boundaries are stored as attributes. """
        for i, m in enumerate(self.all_meshes):
            self.G.add_node(i, cuts=get_existing_cut_indices(m),
                            boundaries=get_existing_boundary_indices(m))

    def get_children_of_node(self, root: int) -> tuple[list[int], list[list[int]]]:
        """
        Find all the nodes that lie on the current root.

        Parameters
        ----------
        root: int, index of root node

        Returns
        ----------
        2 lists [child1, child2, ...], [[common cuts 1], [common cuts 2] ...]
        """
        children: list[int] = []
        cut_ids: list[list[int]] = []
        parent_data = self.G.nodes(data=True)[root]

        for key, data in self.G.nodes(data=True):
            common_cuts = list(set(parent_data['cuts']).intersection(data['cuts']))

            if key != root and len(common_cuts) > 0 \
                    and (key, root) not in self.G.edges() \
                    and (root, key) not in self.G.edges() and is_true_mesh_adjacency(self.all_meshes, key, root):
                if len(common_cuts) != 1:  # if all cuts worked, this should be 1. But life is not perfect.
                    logger.error(
                        f'More than one common cuts between two pieces in the following split meshes. '
                        f'Root : {root}, child : {key} . Common cuts : {common_cuts}'
                        'Probably some cut did not separate components'
                    )
                children.append(key)
                cut_ids.append(common_cuts)

        # --- debugging output
        return children, cut_ids


#################################
#  --- Segments DirectedGraph

class SegmentsDirectedGraph(DirectedGraph):
    """ The SegmentsDirectedGraph is used for topological sorting of multiple vertical_layers_print_data in one mesh"""

    def __init__(
        self, mesh: Mesh, segments: list[VerticalLayer], max_d_threshold: float, DATA_PATH: str
    ) -> None:
        self.mesh = mesh
        self.segments = segments
        self.max_d_threshold = max_d_threshold
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
        DirectedGraph.__init__(self)

    def find_roots(self) -> list[int]:
        """ Roots are vertical_layers_print_data that lie on the build platform. Like that they can be print first. """
        boundary_pts = utils.get_mesh_vertex_coords_with_attribute(self.mesh, 'boundary', 1)
        root_segments: list[int] = []
        for i, segment in enumerate(self.segments):
            first_curve_pts = segment.paths[0].points
            if are_neighboring_point_clouds(boundary_pts, first_curve_pts, 2 * self.max_d_threshold):
                root_segments.append(i)
        return root_segments

    def find_ends(self) -> list[int]:
        """ Ends are vertical_layers_print_data that belong to exclusively one segment. Like that they can be print last. """
        boundary_pts = utils.get_mesh_vertex_coords_with_attribute(self.mesh, 'boundary', 2)
        end_segments: list[int] = []
        for i, segment in enumerate(self.segments):
            last_curve_pts = segment.paths[-1].points
            if are_neighboring_point_clouds(boundary_pts, last_curve_pts, self.max_d_threshold):
                end_segments.append(i)
        return end_segments

    def create_graph_nodes(self) -> None:
        """ Add each segment to to the graph as a node. """
        for i, _segment in enumerate(self.segments):
            self.G.add_node(i)

    def get_children_of_node(self, root: int) -> tuple[list[int], list[None]]:
        """ Find all the nodes that lie on the current root. """
        children: list[int] = []
        root_segment = self.segments[root]
        root_last_crv_pts = root_segment.paths[-1].points
        # utils.save_to_json(utils.point_list_to_dict(root_last_crv_pts), self.OUTPUT_PATH, "root_last_crv_pts.json")

        for i, segment in enumerate(self.segments):
            if i != root:
                segment_first_curve_pts = segment.paths[0].points
                # utils.save_to_json(utils.point_list_to_dict(segment_first_curve_pts), self.OUTPUT_PATH,
                #                    "segment_first_curve_pts.json")
                if are_neighboring_point_clouds(root_last_crv_pts, segment_first_curve_pts, self.max_d_threshold):
                    children.append(i)
        return children, [None for _ in children]  # None because this graph doesn't have cut ids


#################################
# --- helpers

def are_neighboring_point_clouds(pts1: list[Point], pts2: list[Point], threshold: float) -> bool:
    """
    Returns True if 3 or more points of the point clouds are closer than the threshold. False otherwise.

    Parameters
    ----------
    pts1: list, :class: 'compas.geometry.Point'
    pts2: list, :class: 'compas.geometry.Point'
    threshold: float
    """
    if len(pts1) == 0 or len(pts2) == 0:
        return False
    # Vectorized: compute min distance from each pt in pts1 to pts2
    arr1 = np.asarray(pts1, dtype=np.float64)
    arr2 = np.asarray(pts2, dtype=np.float64)
    distances = min_distances_to_set(arr1, arr2)
    return np.sum(distances < threshold) > 5


def is_true_mesh_adjacency(all_meshes: list[Mesh], key1: int, key2: int) -> bool:
    """
    Returns True if the two meshes share 3 or more vertices. False otherwise.

    Parameters
    ----------
    all_meshes: list, :class: 'compas.datastructures.Mesh'
    key1: int, index of mesh1
    key2: int, index of mesh2
    """
    mesh1 = all_meshes[key1]
    mesh2 = all_meshes[key2]
    pts_mesh2 = [mesh2.vertex_coordinates(vkey) for vkey, data in mesh2.vertices(data=True)
                 if (data['cut'] > 0 or data['boundary'] > 0)]
    pts_mesh1 = [mesh1.vertex_coordinates(vkey) for vkey, data in mesh1.vertices(data=True)
                 if (data['cut'] > 0 or data['boundary'] > 0)]
    if len(pts_mesh1) == 0 or len(pts_mesh2) == 0:
        return False
    # Vectorized: compute min distance from each pt in mesh1 to pts_mesh2
    arr1 = np.asarray(pts_mesh1, dtype=np.float64)
    arr2 = np.asarray(pts_mesh2, dtype=np.float64)
    distances = min_distances_to_set(arr1, arr2)
    # Count points with essentially zero distance (shared vertices)
    return np.sum(distances ** 2 < 0.00001) >= 3


if __name__ == '__main__':
    pass
