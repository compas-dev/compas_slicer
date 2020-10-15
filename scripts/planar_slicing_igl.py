import compas
from compas.datastructures import Mesh
from compas.geometry import Point, distance_point_point
from compas_slicer.geometry import Path
from compas_slicer.geometry import Layer
from compas_slicer.utilities import save_to_json
import logging
import numpy as np
import scipy
import networkx as nx

import igl

logger = logging.getLogger('logger')

__all__ = ['create_planar_paths_igl']


def create_planar_paths_igl(mesh, min_z, max_z, planes):

    vs, fi = mesh.to_vertices_and_faces()
    z = [v[2] for v in vs]  # height value

    isoV, isoE = igl.isolines(np.array(vs), np.array(fi), np.array(z), len(planes))

    # create adjacency matrix A
    G = nx.Graph()
    for e in isoE:
        if e[0] != e[1]:
            G.add_edge(*e)
    A = nx.to_scipy_sparse_matrix(G)
    C = igl.connected_components(A)

    print(C[0])
    # print(type(C[0]))
    # print(type(C[1]))
    # print(type(C[2]))

    iso = {}
    iso['isoV'] = [[v[0], v[1], v[2]] for v in isoV]
    iso['isoE'] = [[int(v[0]), int(v[1])] for v in isoE]

    save_to_json(data=iso, filepath='/examples/WIP/3_curved_slicing_surface/data/',
                 name='iso.json')
    print(nx.number_connected_components(G))

    es = {}
    for i, e in enumerate(nx.dfs_edges(G, 3000)):
        print(e)
        es[i] = [int(e[0]), int(e[1])]

    save_to_json(data=es, filepath='/examples/WIP/3_curved_slicing_surface/data/',
                 name='es.json')

    layers = {}
    for j, cp in enumerate(nx.connected_components(G)):
        if j==0:
            print (cp)
        layer = []
        g = nx.Graph();
        for point_index in cp:
            p = isoV[point_index]
            layer.append([p[0], p[1], p[2]])

        layers[j] = layer

    print(layers[0])

    save_to_json(data=layers, filepath ='/examples/WIP/3_curved_slicing_surface/data/', name='isolines.json')

    raise ValueError




if __name__ == "__main__":
    pass
