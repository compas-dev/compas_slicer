from compas.geometry import Point
from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer

from progress.bar import Bar

__all__ = ['create_planar_paths',
           'IntersectionCurveMeshPlane']

import networkx as nx


###################################
### Intersection function
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
### Intersection class
###################################
import logging

from compas.geometry import intersection_segment_plane

logger = logging.getLogger('logger')


# def plot_graph(G):
#     import matplotlib.pyplot as plt
#     plt.subplot(121)
#     nx.draw(G, with_labels=True, font_weight='bold', node_color=range(len(list(G.nodes()))))
#     plt.show()


### --- Class
class IntersectionCurveMeshPlane(object):

    def __init__(self, mesh, plane):
        self.mesh = mesh
        self.plane = plane
        self.intersections = []

        self.intersected_edges = []
        self.intersection_points = {}
        self.ie_indices = {}  # dict that stores node_index and edge relationship
        self.find_intersected_edges()

        self.sorted_point_clusters = {}
        self.sorted_edge_clusters = {}
        self.graph_sorting()

        self.closed_paths_booleans = {}
        self.label_closed_paths()
        # print('Paths are closed: ', self.closed_paths_booleans)

    def label_closed_paths(self):
        for key in self.sorted_edge_clusters:
            first_edge = self.sorted_edge_clusters[key][0]
            last_edge = self.sorted_edge_clusters[key][-1]
            u, v = first_edge
            self.closed_paths_booleans[key] = u in last_edge or v in last_edge

    def edge_is_intersected(self, a, b):
        # check if the plane.z is withing the range of [a.z, b.z]
        z = [a[2], b[2]]
        return min(z) <= self.plane.point[2] <= max(z)

    def find_intersected_edges(self):
        for edge in list(self.mesh.edges()):
            a = self.mesh.vertex_attributes(edge[0], 'xyz')
            b = self.mesh.vertex_attributes(edge[1], 'xyz')

            if self.edge_is_intersected(a, b):
                point = intersection_segment_plane((a, b), self.plane)
                # assert point, 'Attention. Edge is intersected but no intersection point was found.'
                if point:
                    if edge not in self.intersected_edges and tuple(reversed(edge)) not in self.intersected_edges:
                        self.intersected_edges.append(edge)
                        # create [edge - point] dictionary
                        self.intersection_points[edge] = Point(point[0], point[1], point[2]),

            # create [edge - node_index] dictionary
            for i, e in enumerate(self.intersection_points):
                self.ie_indices[e] = i

    def graph_sorting(self):
        # create graph
        G = nx.Graph()
        for i, parent_edge in enumerate(self.intersection_points):
            G.add_node(i, mesh_edge=parent_edge)  # node, attribute

        for node_index, data in G.nodes(data=True):
            mesh_edge = data['mesh_edge']

            # find current neighboring edges
            current_edge_connections = []
            for f in self.mesh.edge_faces(u=mesh_edge[0], v=mesh_edge[1]):
                if f != None:
                    face_edges = self.mesh.face_halfedges(f)
                    for e in face_edges:
                        if (e != mesh_edge and tuple(reversed(e)) != mesh_edge) \
                                and (e in self.intersected_edges or tuple(reversed(e)) in self.intersected_edges):
                            current_edge_connections.append(e)

            for e in current_edge_connections:
                # find other_node_index
                other_node_index = self.ie_indices[e] if e in self.ie_indices else self.ie_indices[tuple(reversed(e))]
                # add edges to the graph (only if the edge doesn't exist already)
                if not G.has_edge(node_index, other_node_index) and not G.has_edge(other_node_index, node_index):
                    G.add_edge(node_index, other_node_index)

        # Graph connected components
        for j, cp in enumerate(nx.connected_components(G)):
            sorted_node_indices = []

            start_node = 0  # find start node_index, can be any edge of the open path
            for node in cp:
                if (len(list(nx.neighbors(G, node)))) == 1:
                    start_node = node
                    break

            # sort nodes_indices with depth first graph traversal from start node
            for edge_of_node_indices in nx.dfs_edges(G, start_node):
                node_index_1 = edge_of_node_indices[0]
                node_index_2 = edge_of_node_indices[1]
                if node_index_1 not in sorted_node_indices:
                    sorted_node_indices.append(node_index_1)
                if node_index_2 not in sorted_node_indices:
                    sorted_node_indices.append(node_index_2)

            assert len(sorted_node_indices) == len(cp), 'Attention. len(sorted_node_indices) != len(G.nodes())'

            # now transform them to the corresponding sorted lists
            self.sorted_point_clusters[j] = []
            self.sorted_edge_clusters[j] = []

            for node_index in sorted_node_indices:
                nodeDict = dict(G.nodes(data=True))
                parent_edge = nodeDict[node_index]['mesh_edge']
                self.sorted_edge_clusters[j].append(parent_edge)

                p = self.intersection_points[parent_edge][0]
                self.sorted_point_clusters[j].append(p)

