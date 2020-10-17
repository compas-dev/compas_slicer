import networkx as nx

__all__ = ['create_graph_from_mesh_edges',
           'sort_graph_connected_components',
           'create_graph_from_mesh_vkeys']


def create_graph_from_mesh_edges(mesh, intersected_edges,
                                 intersection_points,
                                 edge_point_index_relation):
    # create graph
    G = nx.Graph()
    for i, parent_edge in enumerate(intersection_points):
        G.add_node(i, mesh_edge=parent_edge)  # node, attribute

    for node_index, data in G.nodes(data=True):
        mesh_edge = data['mesh_edge']

        # find current neighboring edges
        current_edge_connections = []
        for f in mesh.edge_faces(u=mesh_edge[0], v=mesh_edge[1]):
            if f is not None:
                face_edges = mesh.face_halfedges(f)
                for e in face_edges:
                    if (e != mesh_edge and tuple(reversed(e)) != mesh_edge) \
                            and (e in intersected_edges or tuple(reversed(e)) in intersected_edges):
                        current_edge_connections.append(e)

        for e in current_edge_connections:
            # find other_node_index
            other_node_index = edge_point_index_relation[e] if e in edge_point_index_relation \
                else edge_point_index_relation[tuple(reversed(e))]
            # add edges to the graph (only if the edge doesn't exist already)
            if not G.has_edge(node_index, other_node_index) and not G.has_edge(other_node_index, node_index):
                G.add_edge(node_index, other_node_index)
    return G


def create_graph_from_mesh_vkeys(mesh, v_keys):
    G = nx.Graph()
    [G.add_node(v) for v in v_keys]
    for v in v_keys:
        v_neighbors = mesh.vertex_neighbors(v)
        for other_v in v_neighbors:
            if other_v != v and other_v in v_keys:
                G.add_edge(v, other_v)
    return G


def sort_graph_connected_components(G, intersection_points):
    sorted_point_clusters = {}
    sorted_edge_clusters = {}

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
        sorted_point_clusters[j] = []
        sorted_edge_clusters[j] = []

        for node_index in sorted_node_indices:
            nodeDict = dict(G.nodes(data=True))
            parent_edge = nodeDict[node_index]['mesh_edge']
            sorted_edge_clusters[j].append(parent_edge)

            p = intersection_points[parent_edge][0]
            sorted_point_clusters[j].append(p)
    return sorted_point_clusters, sorted_edge_clusters



