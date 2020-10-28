import numpy as np
import scipy
import math
from compas.datastructures import Mesh
import compas_slicer.utilities as utils
import logging
import networkx as nx
from compas_slicer.slicers.slice_utilities import create_graph_from_mesh_vkeys
from compas_slicer.pre_processing.curved_slicing_preprocessing.geodesics import get_igl_EXACT_geodesic_distances, \
    get_custom_HEAT_geodesic_distances

packages = utils.TerminalCommand('conda list').get_split_output_strings()
if 'igl' in packages:
    import igl

logger = logging.getLogger('logger')

__all__ = ['CompoundTarget']


class CompoundTarget:
    """
    CompoundTarget is represents a desired user-provided target. It acts as a key-frame that controls the print paths
    orientations. After the curved slicing , the print paths will be aligned to the compound target close to
    its area.

    Attributes
    ----------
    mesh : :class:`compas.datastructures.Mesh`
    v_attr : str
        The key of the attribute dict to be checked.
    value : int
        The value of the attribute dict with key=v_attr. If in a vertex data[v_attr]==value then the vertex is part of
        this target.
    DATA_PATH : str
    is_smooth : bool
    r : float
    geodesics_method : str
        'exact' is the only method currently implemented
    anisotropic_scaling : bool
        This is not yet implemented
    """

    def __init__(self, mesh, v_attr, value, DATA_PATH, is_smooth=False, r=15.0,
                 geodesics_method='exact', anisotropic_scaling=False):

        self.mesh = mesh
        self.v_attr = v_attr
        self.value = value
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
        self.is_smooth = is_smooth
        self.r = r

        self.geodesics_method = geodesics_method
        self.anisotropic_scaling = anisotropic_scaling  # Anisotropic scaling not yet implemented

        self.L = None

        self.offset = 0
        self.VN = len(list(self.mesh.vertices()))

        # targets connected components
        self.all_target_vkeys = []  # flattened list with all vi_starts
        self.clustered_vkeys = []  # nested list with all vi_starts
        self.number_of_boundaries = None  # int

        # geodesic distances
        # SHOULD NOT BE WRITTEN DIRECTLY! ONLY THROUGH THE METHOD 'update_distances_lists'
        self.distances_lists = []  # nested list. Shape: number_of_boundaries x number_of_vertices
        self.distances_lists_flipped = []  # nested list. Shape: number_of_vertices x number_of_boundaries
        self.np_distances_lists_flipped = np.array([])  # numpy array of self.distances_lists_flipped
        self.max_dist = None  # maximum distance value from the target on any vertex of the mesh

        self.t_end_per_cluster = []

        self.find_targets_connected_components()
        self.compute_geodesic_distances()

    #############################
    #  --- Clustering
    def find_targets_connected_components(self):
        self.all_target_vkeys = [vkey for vkey, data in self.mesh.vertices(data=True) if
                                 data[self.v_attr] == self.value]
        assert len(self.all_target_vkeys) > 0, "There are no vertices in the mesh with the attribute : " \
                                               + self.v_attr + ", value : %d" % self.value
        G = create_graph_from_mesh_vkeys(self.mesh, self.all_target_vkeys)
        assert len(list(G.nodes())) == len(self.all_target_vkeys)
        self.number_of_boundaries = len(list(nx.connected_components(G)))

        for i, cp in enumerate(nx.connected_components(G)):
            self.clustered_vkeys.append(list(cp))
        logger.info('Compound target with value : %d. Number of targets : %d' % (
            self.value, len(list(nx.connected_components(G)))))

    #############################
    #  --- Geodesic distances
    def compute_geodesic_distances(self):
        if self.geodesics_method == 'exact':
            distances_lists = [get_igl_EXACT_geodesic_distances(self.mesh, vstarts) for vstarts in
                               self.clustered_vkeys]
        elif self.geodesics_method == 'heat':
            raise NotImplementedError
        else:
            raise ValueError('Unknown geodesics method : ' + self.geodesics_method)

        distances_lists = [list(dl) for dl in distances_lists]  # number_of_boundaries x #V
        self.update_distances_lists(distances_lists)

    def update_distances_lists(self, distances_lists):
        self.distances_lists = distances_lists
        self.distances_lists_flipped = []  # empty
        for i in range(self.VN):
            current_values = [self.distances_lists[list_index][i] for list_index in range(self.number_of_boundaries)]
            self.distances_lists_flipped.append(current_values)
        self.np_distances_lists_flipped = np.array(self.distances_lists_flipped)
        self.max_dist = np.max(self.np_distances_lists_flipped)

    # ---- Uneven boundaries
    def compute_uneven_boundaries_t_ends(self, other_target):
        if self.number_of_boundaries > 1:
            ds_avg_HIGH = self.get_boundaries_avg_dist_from_other_target(other_target)

            for i, d in enumerate(ds_avg_HIGH):  # offset all distances except the maximum one
                if abs(d - max(ds_avg_HIGH)) > 0.01:  # if it isn't the max value
                    ds_avg_HIGH[i] = d + self.offset

            self.t_end_per_cluster = [d / max(ds_avg_HIGH) for d in ds_avg_HIGH]
            logger.info('t_end_per_cluster : ' + str(self.t_end_per_cluster))
        else:
            logger.info("Did not compute_norm_of_gradient uneven boundaries, target consists of single component")

    def use_uneven_weights(self):
        return len(self.t_end_per_cluster) > 0

    #############################
    #  --- Relation to other target
    def get_boundaries_avg_dist_from_other_target(self, other_target):
        """ Returns a list, one avg distance value per connected boundary"""
        ds_avg = []
        for vi_starts in self.clustered_vkeys:
            d_avg = 0
            for vi in vi_starts:
                d_avg += other_target.distance(vi)
            ds_avg.append(d_avg / len(vi_starts))
        return ds_avg

    def get_extreme_distances_from_other_target(self, other_target):
        extreme_distances = []
        for v_index in other_target.all_target_vkeys:
            extreme_distances.append(self.all_distances()[v_index])
        return min(extreme_distances), max(extreme_distances)

    #############################
    #  --- get distances

    def all_clusters_distances(self, i):
        return [self.distances_lists[list_index][i] for list_index in range(self.number_of_boundaries)]

    def distance(self, i):
        return self.smooth_union(i) if self.is_smooth else self.union(i)

    def union(self, i):
        return np.min(self.np_distances_lists_flipped[i])

    def smooth_union(self, i):
        d = None
        for other_d in self.np_distances_lists_flipped[i]:
            d = smooth_union(d, other_d, self.r) if d else other_d
        return d

    def all_distances(self):
        return [self.distance(i) for i in range(self.VN)]

    #############################
    #  --- distance smoothing

    def get_laplacian(self, fix_boundaries=True):
        logger.info('Getting laplacian matrix, fix boundaries : ' + str(fix_boundaries))
        v, f = self.mesh.to_vertices_and_faces()
        L = igl.cotmatrix(np.array(v), np.array(f))

        if fix_boundaries:
            # fix boundaries by putting the corresponding columns of the sparse matrix to 0, diagonal stays to 1
            L_dense = L.toarray()
            for i, (vkey, data) in enumerate(self.mesh.vertices(data=True)):
                if data['boundary'] > 0:
                    a = np.zeros(self.VN)
                    a[i] = 1  # set the diagonal to 1
                    L_dense[i][:] = a
            L = scipy.sparse.csr_matrix(L_dense)
        return L

    def laplacian_smoothing_of_all_distances(self, iterations, lamda):
        if not self.L:
            self.L = self.get_laplacian()

        new_distances_lists = []

        logger.info('Laplacian smoothing of all distances')
        for i, a in enumerate(self.distances_lists):
            print('Smoothing list of distances with index %d' % i)  # iterative smoothing
            a = np.array(a)  # a: numpy array containing the attribute to be smoothed
            for _ in range(iterations):
                a_prime = a + lamda * self.L * a
                a = a_prime

            new_distances_lists.append(list(a))

        self.update_distances_lists(new_distances_lists)

    #############################
    #  ------ output
    def save_distances(self, name):
        utils.save_to_json(self.all_distances(), self.OUTPUT_PATH, name)

    def save_distances_clusters(self, name):
        clusters_distances = {}
        for list_index in range(self.number_of_boundaries):
            clusters_distances[list_index] = []

        for i in range(self.VN):
            all_ds = self.all_clusters_distances(i)
            for j, d in enumerate(all_ds):
                clusters_distances[j].append(d)
        utils.save_to_json(clusters_distances, self.OUTPUT_PATH, name)

    def save_start_vertices(self, name):
        utils.save_to_json([int(vi) for vi in self.all_target_vkeys], self.OUTPUT_PATH, name)

    #############################
    #  ------ assign new Mesh
    def assign_new_mesh(self, mesh):
        mesh.to_json(self.OUTPUT_PATH + "/temp.obj")
        mesh = Mesh.from_json(self.OUTPUT_PATH + "/temp.obj")
        self.mesh = mesh
        self.VN = len(list(self.mesh.vertices()))


####################
#  utils

def smooth_union(da, db, r):
    #  smooth union
    e = max(r - abs(da - db), 0)
    return min(da, db) - e * e * 0.25 / r


def champfer_union(da, db, r):
    # champfer
    m = min(da, db)
    if m > (da ** 2 + db ** 2 - r ** 2) * math.sqrt(0.5):
        print('here')
    return min(m, (da ** 2 + db ** 2 - r ** 2) * math.sqrt(0.5))


if __name__ == "__main__":
    pass
