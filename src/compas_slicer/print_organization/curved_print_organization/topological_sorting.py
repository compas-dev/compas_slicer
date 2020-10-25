import networkx as nx
from compas.geometry import distance_point_point_sqrd
import compas_slicer.utilities as utils
import logging
import copy
from compas_slicer.pre_processing.curved_slicing_preprocessing import get_existing_cut_indices, get_existing_boundary_indices
from abc import abstractmethod

logger = logging.getLogger('logger')

__all__ = ['MeshDirectedGraph',
           'SegmentsDirectedGraph']


#################################
#  DirectedGraph

class DirectedGraph(object):
    """
    Base class for topological sorting of prints that consist of several parts that lie on each other.
    For example the graph A->B->C would represent a print that consists of three parts; A, B, C
    where A lies on the build platform, B lies on A, and C lies on B.
    This graph cannot have cycles; cycles would represent an unfeasible print.
    """

    def __init__(self):
        logger.info('Topological sorting')

        self.G = nx.DiGraph()
        self.create_graph_nodes()
        self.root_indices = self.find_roots()
        self.create_directed_graph_edges(copy.deepcopy(self.root_indices))
        logger.info('Nodes : ' + str(self.G.nodes(data=True)))
        logger.info('Edges : ' + str(self.G.edges(data=True)))

        self.N = len(list(self.G.nodes()))
        self.adj_list = self.get_adjacency_list()
        self.check_that_all_nodes_found_their_connectivity()
        logger.info('Adjacency list : ' + str(self.adj_list))
        self.in_degree = self.get_in_degree()
        self.all_orders = []

    def __repr__(self):
        return "<DirectedGraph with %i nodes>" % len(list(self.G.nodes()))

    # ------------------------------------ Methods to be implemented by inheriting classes
    @abstractmethod
    def find_roots(self):
        """Roots are segments that lie on the build platform, i.e. they can be print first"""
        pass

    @abstractmethod
    def create_graph_nodes(self):
        """Add the nodes to the graph with their attributes"""
        pass

    @abstractmethod
    def get_children_of_node(self, root):
        """Find all the segments that lie on the current root segment"""
        pass

    # ------------------------------------ Creation of graph connectivity between different nodes
    def create_directed_graph_edges(self, root_indices):
        passed_nodes = []
        queue = root_indices

        while len(queue) > 0:
            current_node = queue[0]
            queue.remove(current_node)
            passed_nodes.append(current_node)
            children, cut_ids = self.get_children_of_node(current_node)
            [self.G.add_edge(current_node, child_key, cut=cut_id) for child_key, cut_id in zip(children, cut_ids)]
            for child_key in children:
                assert child_key not in passed_nodes, 'Error, cyclic directed graph.'
            [queue.append(child_key) for child_key in children if child_key not in queue]

    def check_that_all_nodes_found_their_connectivity(self):
        good_nodes = [r for r in self.root_indices]
        for children_list in self.adj_list:
            [good_nodes.append(child) for child in children_list if child not in good_nodes]
        assert len(good_nodes) == self.N, 'There are floating segments on directed graph. Investigate the process of \
                                          the creation of the graph. '

    # ------------------------------------ Find all topological orders
    def get_adjacency_list(self):
        adj_list = [[] for _ in range(self.N)]  # adjacency list , size = len(Nodes), stores nodes' neighbors
        for i, adjacent_to_node in self.G.adjacency():
            [adj_list[i].append(key) for key in adjacent_to_node]
        return adj_list

    def get_in_degree(self):
        in_degree = [0] * self.N  # in_degree,  size = len(Nodes) , stores in-degree of a node
        for key_degree_tuple in self.G.in_degree:
            key = key_degree_tuple[0]
            degree = key_degree_tuple[1]
            in_degree[key] = degree
        return in_degree

    def get_all_topological_orders(self):
        self.all_orders = []  # make sure list is empty
        discovered = [False] * self.N
        path = []  # list to store the topological order
        self.get_orders(path, discovered)
        logger.info('Found %d possible orders' % len(self.all_orders))
        return self.all_orders

    def get_orders(self, path, discovered):
        # Sorting algorithm taken from https://www.techiedelight.com/find-all-possible-topological-orderings-of-dag/
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

    def get_parents_of_node(self, node_index):
        return [j for j, adj in enumerate(self.adj_list) if node_index in adj]


#################################
#  --- Meshes DirectedGraph

class MeshDirectedGraph(DirectedGraph):
    """ The MeshDirectedGraph is used for topological sorting of multiple meshes that have been
    generated as a result of region split over the saddle points of the mesh scalar function """

    def __init__(self, all_meshes):
        self.all_meshes = all_meshes
        DirectedGraph.__init__(self)

    def find_roots(self):
        roots = []
        for i, mesh in enumerate(self.all_meshes):
            for vkey, data in mesh.vertices(data=True):
                if i not in roots:
                    if data['boundary'] == 1:
                        roots.append(i)
        return roots

    def create_graph_nodes(self):
        # initialize graph Meshes as nodes. Cuts and boundaries as attributes
        for i, m in enumerate(self.all_meshes):
            self.G.add_node(i, cuts=get_existing_cut_indices(m),
                            boundaries=get_existing_boundary_indices(m))

    def get_children_of_node(self, root):
        children = []
        cut_ids = []
        parent_data = self.G.nodes(data=True)[root]

        for key, data in self.G.nodes(data=True):
            common_cuts = list(set(parent_data['cuts']).intersection(data['cuts']))

            if key != root and len(common_cuts) > 0 \
                    and (key, root) not in self.G.edges() \
                    and (root, key) not in self.G.edges():
                if is_true_mesh_adjacency(self.all_meshes, key, root):
                    # try:
                    assert len(common_cuts) == 1
                    # except: logger.error('More than one common cuts between two pieces in the following split
                    # meshes. ' 'Root : %d, child : %d' % (root, key) + ' . Common cuts : ' + str(common_cuts)) #
                    # TODO: improve this. Two meshes COULD have more common cuts, resulting for example from
                    #  one-vertex connections raise ValueError

                    children.append(key)
                    cut_ids.append(common_cuts[0])
        return children, cut_ids


#################################
#  Segments DirectedGraph


class SegmentsDirectedGraph(DirectedGraph):
    """ The SegmentsDirectedGraph is used for topological sorting of multiple segments in one mesh"""

    def __init__(self, mesh, segments, max_d_threshold, DATA_PATH):
        self.mesh = mesh
        self.segments = segments
        self.max_d_threshold = max_d_threshold
        self.DATA_PATH = DATA_PATH
        DirectedGraph.__init__(self)

    def find_roots(self):
        boundary_pts = utils.get_mesh_vertex_coords_with_attribute(self.mesh, 'boundary', 1)
        root_segments = []
        for i, segment in enumerate(self.segments):
            first_curve_pts = segment.paths[0].points
            if are_neighboring_point_clouds(boundary_pts, first_curve_pts, self.max_d_threshold):
                root_segments.append(i)
        logger.info('Graph roots : ' + str(root_segments))
        return root_segments

    def create_graph_nodes(self):
        # initialize graph Meshes as nodes. Cuts and boundaries as attributes
        for i, segment in enumerate(self.segments):
            self.G.add_node(i)

    def get_children_of_node(self, root):
        children = []
        root_segment = self.segments[root]
        root_last_crv_pts = root_segment.paths[-1].points

        # utils.save_to_json(utils.point_list_to_dict(root_last_crv_pts), self.DATA_PATH, 'root_last_crv_pts.json')
        for i, segment in enumerate(self.segments):
            if i != root:
                segment_first_curve_pts = segment.paths[0].points
                # utils.save_to_json(utils.point_list_to_dict(segment_first_curve_pts), self.DATA_PATH,
                #                    'segment_first_curve_pts.json')
                # utils.interrupt()

                if are_neighboring_point_clouds(root_last_crv_pts, segment_first_curve_pts, self.max_d_threshold):
                    children.append(i)
        return children, [None for _ in children]  # this graph doesn't have cut ids


#################################
# --- helpers

def are_neighboring_point_clouds(pts1, pts2, threshold):
    count = 0
    for pt in pts1:
        if distance_point_point_sqrd(pt, utils.get_closest_pt(pt, pts2)) < threshold:
            count += 1
            if count > 3:
                return True
    return False


def is_true_mesh_adjacency(all_meshes, key1, key2):
    count = 0
    mesh1 = all_meshes[key1]
    mesh2 = all_meshes[key2]
    pts_mesh2 = [mesh2.vertex_coordinates(vkey) for vkey, data in mesh2.vertices(data=True)
                 if (data['cut'] > 0 or data['boundary'] > 0)]
    for vkey, data in mesh1.vertices(data=True):
        if data['cut'] > 0 or data['boundary'] > 0:
            pt = mesh1.vertex_coordinates(vkey)
            ci = utils.get_closest_pt_index(pt, pts_mesh2)
            if distance_point_point_sqrd(pt, pts_mesh2[ci]) < 0.00001:
                count += 1
                if count == 3:
                    # TODO: improve this. Two meshes could have 3 one-vertex-connections for example.
                    #        Also two meshes could have only two vertex connection and depend on each other.
                    return True
    return False


if __name__ == '__main__':
    pass
