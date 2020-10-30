import numpy as np
import scipy
from compas.datastructures import Mesh
import compas_slicer.utilities as utils
import logging
import networkx as nx
from compas_slicer.slicers.slice_utilities import create_graph_from_mesh_vkeys
from compas_slicer.pre_processing.curved_slicing_preprocessing.geodesics import get_igl_EXACT_geodesic_distances
import statistics

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
    geodesics_method : str
        'exact' is the only method currently implemented
    anisotropic_scaling : bool
        This is not yet implemented
    """

    def __init__(self, mesh, v_attr, value, DATA_PATH,
                 geodesics_method='exact', anisotropic_scaling=False):

        self.mesh = mesh
        self.v_attr = v_attr
        self.value = value
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)

        self.geodesics_method = geodesics_method
        self.anisotropic_scaling = anisotropic_scaling  # Anisotropic scaling not yet implemented

        self.L = None

        self.offset = 20
        self.VN = len(list(self.mesh.vertices()))

        # targets connected components
        self.all_target_vkeys = []  # flattened list with all vi_starts
        self.clustered_vkeys = []  # nested list with all vi_starts
        self.number_of_boundaries = None  # int

        # geodesic distances
        # These parameters SHOULD NOT BE WRITTEN DIRECTLY! ONLY THROUGH THE METHOD 'update_distances_lists'
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
            ds_avg_HIGH = self.get_boundaries_rel_dist_from_other_target(other_target)

            for i, d in enumerate(ds_avg_HIGH):  # offset all distances except the maximum one
                if abs(d - max(ds_avg_HIGH)) > 0.01:  # if it isn't the max value
                    ds_avg_HIGH[i] = d + self.offset

            self.t_end_per_cluster = [d / max(ds_avg_HIGH) for d in ds_avg_HIGH]
            logger.info('t_end_per_cluster : ' + str(self.t_end_per_cluster))
        else:
            logger.info("Did not compute_norm_of_gradient uneven boundaries, target consists of single component")

    @property
    def has_uneven_weights(self):
        return len(self.t_end_per_cluster) > 0

    #############################
    #  --- Relation to other target
    def get_boundaries_rel_dist_from_other_target(self, other_target, type='median'):
        """ Returns a list, one relative distance value per connected boundary"""
        distances = []
        for vi_starts in self.clustered_vkeys:
            ds = [other_target.distance(vi) for vi in vi_starts]
            if type == 'mean':
                distances.append(statistics.mean(ds))
            else:  # 'median'
                distances.append(statistics.median(ds))
        return distances

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
        return self.union(i)

    def union(self, i):
        return np.min(self.np_distances_lists_flipped[i])

    def all_distances(self):
        return [self.distance(i) for i in range(self.VN)]

    #############################
    #  --- distance smoothing

    def get_laplacian(self, fix_boundaries=True):
        logger.info('Getting laplacian matrix, fix boundaries : ' + str(fix_boundaries))
        v, f = self.mesh.to_vertices_and_faces()
        L = igl.cotmatrix(np.array(v), np.array(f))

        if fix_boundaries:
            # fix boundaries by putting the corresponding columns of the sparse matrix to 0
            L_dense = L.toarray()
            for i, (vkey, data) in enumerate(self.mesh.vertices(data=True)):
                if data['boundary'] > 0:
                    L_dense[i][:] = np.zeros(self.VN)
            L = scipy.sparse.csr_matrix(L_dense)

        return L

    def laplacian_smoothing(self, iterations, lamda):
        if not self.L:
            self.L = self.get_laplacian()
        new_distances_lists = []

        logger.info('Laplacian smoothing of all distances')
        for i, a in enumerate(self.distances_lists):
            a = np.array(a)  # a: numpy array containing the attribute to be smoothed
            for _ in range(iterations):  # iterative smoothing
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


if __name__ == "__main__":
    pass
