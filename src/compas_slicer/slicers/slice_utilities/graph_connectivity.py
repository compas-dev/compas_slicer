import networkx as nx

__all__ = ['create_graph_from_mesh_edges',
           'sort_graph_connected_components',
           'create_graph_from_mesh_vkeys']


def create_graph_from_mesh_edges(mesh, intersection_data, edge_to_index):
    """
    Creates a graph with one node for every intersected edge.
    The connectivity of nodes (i.e. edges between them) is based on their neighboring on the mesh.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    intersection_data: dict, (ui,vi) : {'pt':[xi,yi,zi], 'attrs':{...}}
        The keys-tuples are all the edges which have a zero crossing.
    edge_to_index: dict
        key: tuple (int, int) edge
        value: int, index of the intersection point

    Returns
    ----------
    G: :class: 'networkx.Graph'. Node_indices > intersection indices. Node_attrs > their parent_edges (i.e. the keys of
        the intersection_data dict)
    """

    # create graph
    G = nx.Graph()
    for i, edge in enumerate(intersection_data):
        G.add_node(i, mesh_edge=edge)  # node, attribute

    for node_index, data in G.nodes(data=True):
        mesh_edge = data['mesh_edge']

        # find current neighboring edges that are also intersected
        current_edge_connections = []
        for f in mesh.edge_faces(u=mesh_edge[0], v=mesh_edge[1]):
            if f is not None:
                face_edges = mesh.face_halfedges(f)
                for e in face_edges:
                    if (e != mesh_edge and tuple(reversed(e)) != mesh_edge) \
                            and (e in intersection_data or tuple(reversed(e)) in intersection_data):
                        current_edge_connections.append(e)

        for e in current_edge_connections:
            # find other_node_index
            other_node_index = edge_to_index[e] if e in edge_to_index \
                else edge_to_index[tuple(reversed(e))]
            # add edges to the graph (only if the edge doesn't exist already)
            if not G.has_edge(node_index, other_node_index) and not G.has_edge(other_node_index, node_index):
                G.add_edge(node_index, other_node_index)

    return G


def create_graph_from_mesh_vkeys(mesh, v_keys):
    """
    Creates a graph with one node for every vertex, and edges between neighboring vertices.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    v_keys: list int
        The vertex keys

    Returns
    ----------
    G: :class: 'networkx.Graph'
    """
    G = nx.Graph()
    [G.add_node(v) for v in v_keys]
    for v in v_keys:
        v_neighbors = mesh.vertex_neighbors(v)
        for other_v in v_neighbors:
            if other_v != v and other_v in v_keys:
                G.add_edge(v, other_v)
    return G


def sort_graph_connected_components(G):
    """
    For every connected component of the graph G:
    1) It finds a start node. For open paths it is on one of its ends, for closed paths it can be any of its points.
    2) It sorts all nodes starting from the start using depth first graph traversal.
    3) Using this sorted order, it sorts the intersected edges and zero-crossing points that are linked to the graph G.

    Parameters
    ----------
    G: :class: 'networkx.Graph', Node_indices > intersection point indices. Node_attrs > parent_edges

    Returns
    ----------
    sorted_point_clusters: dict
        key: int, The index of the connected component
        value: list, :class: 'compas.geometry.Point', The sorted zero-crossing points.
    sorted_edge_clusters: dict
        key: int, The index of the connected component.
        value: list, tuple (int, int), The sorted intersected edges.
    """

    sorted_indices_dict = {}

    current_index = 0

    for j, cp in enumerate(nx.connected_components(G)):

        if len(cp) > 1:  # we need at least 2 elements to have an edge
            sorted_node_indices = []

            # (1) find start_node index
            start_node = None
            for node in cp:
                if not start_node:
                    start_node = node
                if (len(list(nx.neighbors(G, node)))) == 1:
                    start_node = node
                    break

            # (2) sort nodes_indices with depth first graph traversal from start node
            for edge_of_node_indices in nx.dfs_edges(G, start_node):
                # edge_of_node_indices: pair of neighboring graph nodes
                node_index_1 = edge_of_node_indices[0]
                node_index_2 = edge_of_node_indices[1]
                if node_index_1 not in sorted_node_indices:
                    sorted_node_indices.append(node_index_1)
                if node_index_2 not in sorted_node_indices:
                    sorted_node_indices.append(node_index_2)

            assert len(sorted_node_indices) == len(cp), 'Attention. len(sorted_node_indices) != len(G.nodes())'

            sorted_indices_dict[current_index] = sorted_node_indices
            current_index += 1

    return sorted_indices_dict
