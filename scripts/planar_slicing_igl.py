import itertools
from compas.geometry import Point, distance_point_point_sqrd
from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path
import numpy as np
import copy
import networkx as nx
import logging
import compas_slicer.utilities as utils
from compas_slicer.slicers.slice_utilities import sort_graph_connected_components
import progressbar

__all__ = ['create_planar_paths_igl']

logger = logging.getLogger('logger')


def try_to_create_connection(G, isoV, ei, ej, i, j, side_i, side_j, connections_found, tol):
    vi = isoV[ei[side_i]]
    vj = isoV[ej[side_j]]
    if distance_point_point_sqrd(vi, vj) < tol:
        G.add_edge(i, j)
        connections_found[i][side_i] = True
        connections_found[j][side_j] = True
        return True
    return False

def create_planar_paths_igl(mesh, n):
    """
    Creates planar contours using the libigl function: https://libigl.github.io/libigl-python-bindings/igl_docs/#isolines
    TODO: ??? It is currently the only method that can return identify OPEN versus CLOSED paths.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
        The mesh to be sliced
    n: number of contours
    """
    # utils.check_package_is_installed('igl')
    import igl
    v, f = mesh.to_vertices_and_faces()

    ds = np.array([vertex[2] for vertex in v])
    # save distances of each vertex from the floor: this will be the scalar field for the slicing operation.

    # --- generate disconnected segments of isolines using the libigl function
    v = np.array(v)
    f = np.array(f)
    isoV, isoE = igl.isolines(v, f, ds, n)

    # --- group resulting segments per level
    print('Grouping segments per level')
    segments_per_level = {}
    tol = 1e-6
    for e in isoE:
        v0 = isoV[e[0]]
        v1 = isoV[e[1]]
        assert(abs(v0[2] - v1[2]) < tol)
        h = v0[2]

        found = False
        for key in segments_per_level:
            if abs(key - h) < tol:
                if e[0] != e[1]:  # do not add null segments
                    segments_per_level[key].append(e)
                    found = True

        if not found:
            segments_per_level[h] = [e]

    #assert(len(segments_per_level) == n)

    utils.save_to_json(utils.point_list_to_dict(isoV), "/examples/1_planar_slicing_simple/data/output", 'isoV.json')

    sorted_keys = [key for key in segments_per_level]
    sorted(sorted_keys)

    layers = []

    # --- Create connectivity graph G for every group, and sort edges based on G
    with progressbar.ProgressBar(max_value=len(segments_per_level)) as bar:
        for index, key in enumerate(sorted_keys):
            #print(' Creating connectivity for level z = ', key)

            es = segments_per_level[key]  # list of the current edges, which whose indices we are working below

            G = nx.Graph()

            connections_found = [[False, False] for _ in es]

            for i, e in enumerate(es):
                G.add_node(i)  # node, attribute

            for i, ei in enumerate(es):  # ei here is the edge, not the index!
                for side_i in range(2):
                    if not connections_found[i][side_i]:
                        for jj, ej in enumerate(es[i+1:]):  # ej here is the edge, not the index!
                            j = i + jj + 1
                            for side_j in range(2):
                                if not connections_found[j][side_j]:
                                    vi = isoV[ei[side_i]]
                                    vj = isoV[ej[side_j]]
                                    if distance_point_point_sqrd(vi, vj) < tol:
                                        G.add_edge(i, j)
                                        connections_found[i][side_i] = True
                                        connections_found[j][side_j] = True

            # sort connected components of G
            sorted_indices_dict = sort_graph_connected_components(G)

            # for i, s_key in enumerate(sorted_indices_dict):
            #     sorted_eis = sorted_indices_dict[s_key]
            #     this_segment_pts = []
            #
            #     for j, ei in enumerate(sorted_eis):
            #         e = es[ei]
            #         # segment pts
            #         for k in range(2):
            #             this_segment_pts.append(isoV[e[k]])
            #
            #     utils.save_to_json(utils.point_list_to_dict(this_segment_pts),
            #                        "C:/dev/compas_slicer/examples/1_planar_slicing_simple/data/output", 'isoV.json')
            #     print('saved')

            # get points list from sorted edge indices (for each connected component)
            paths_pts = [[] for _ in sorted_indices_dict]
            are_closed = [True for _ in sorted_indices_dict]
            for i, s_key in enumerate(sorted_indices_dict):
                sorted_indices = sorted_indices_dict[s_key]

                for j, s_ei in enumerate(sorted_indices):
                    v0 = isoV[es[s_ei][0]]
                    v1 = isoV[es[s_ei][1]]
                    if j == 0:
                        s_ei_next = sorted_indices[j+1]
                        v0_next = isoV[es[s_ei_next][0]]
                        v1_next = isoV[es[s_ei_next][1]]
                        v_mid_next = (Point(*v0_next) + Point(*v1_next)) * 0.5
                        if distance_point_point_sqrd(v0, v_mid_next) < distance_point_point_sqrd(v1, v_mid_next):
                            paths_pts[i].extend([Point(*v1), Point(*v0)])
                        else:
                            paths_pts[i].extend([Point(*v0), Point(*v1)])

                    else:
                        v_prev = paths_pts[i][-1]
                        if distance_point_point_sqrd(v0, v_prev) < distance_point_point_sqrd(v1, v_prev):
                            paths_pts[i].append(Point(*v1))
                        else:
                            paths_pts[i].append(Point(*v0))

                if distance_point_point_sqrd(paths_pts[i][0], paths_pts[i][1]) > tol:
                    are_closed[i] = False

            paths = []
            for i in range(len(sorted_indices_dict)):
                paths.append(Path(points=paths_pts[i], is_closed=are_closed[i]))

            layers.append(Layer(paths))
            bar.update(index)

    return layers
