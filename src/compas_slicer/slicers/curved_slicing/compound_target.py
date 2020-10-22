import numpy as np
import math
from compas_slicer.utilities import TerminalCommand
import compas_slicer.utilities as utils
import logging
import networkx as nx
from compas_slicer.slicers.slice_utilities import create_graph_from_mesh_vkeys

packages = TerminalCommand('conda list').get_split_output_strings()
if 'igl' in packages:
    import igl

logger = logging.getLogger('logger')

__all__ = ['CompoundTarget']


class CompoundTarget:
    """
    CompoundTarget is...

    Attributes
    ----------
    params : Fill things in!
    """

    def __init__(self, mesh, v_attr, value, DATA_PATH, is_smooth=False, r=15.0,
                 geodesics_method='exact', anisotropic_scaling=False):

        self.mesh = mesh
        self.v_attr = v_attr
        self.value = value
        self.DATA_PATH = DATA_PATH
        self.is_smooth = is_smooth
        self.r = r

        self.geodesics_method = geodesics_method
        self.anisotropic_scaling = anisotropic_scaling

        self.offset = 0
        self.VN = len(list(self.mesh.vertices()))
        self.distances_lists = []  # list of lists: number_of_boundaries x #V
        self.all_target_vkeys = []  # flattened list with all vi_starts
        self.clustered_vkeys = []  # nested list with all vi_starts
        self.number_of_boundaries = None

        self.t_end_per_cluster = []

        self.OVERWRITE_all_distances = []  # stores Laplacian smoothing distances if used

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
            distances_lists = [utils.get_igl_EXACT_geodesic_distances(self.mesh, vstarts) for vstarts in
                               self.clustered_vkeys]

        elif self.geodesics_method == 'heat':
            distances_lists = [utils.get_custom_HEAT_geodesic_distances(self.mesh, vstarts, self.DATA_PATH,
                                                                        anisotropic_scaling=self.anisotropic_scaling)
                               for vstarts in self.clustered_vkeys]
        else:
            raise ValueError('Unknown geodesics method : ' + self.geodesics_method)

        self.distances_lists = [list(dl) for dl in distances_lists]  # list of lists

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
            logger.info("Did not compute_distance_speed_scalar uneven boundaries, target consists of single component")

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
        if len(self.OVERWRITE_all_distances) == 0:
            if self.is_smooth:
                return self.smooth_union(i)
            else:
                return self.union(i)
        else:
            return self.OVERWRITE_all_distances[i]

    def union(self, i):
        d = self.distances_lists[0][i]
        for list_index in range(self.number_of_boundaries):
            if list_index > 0:
                d = min(d, self.distances_lists[list_index][i])
        return d

    def smooth_union(self, i):
        d = self.distances_lists[0][i]
        for list_index in range(self.number_of_boundaries):
            if list_index > 0:
                d = smooth_union(d, self.distances_lists[list_index][i], self.r)
        return d

    def all_distances(self):
        if self.is_smooth:
            return [self.smooth_union(i) for i in range(self.VN)]
        else:
            return [self.union(i) for i in range(self.VN)]

    def laplacian_smoothing_of_all_distances(self, iterations, lamda):
        v, f = self.mesh.to_vertices_and_faces()
        L = igl.cotmatrix(np.array(v), np.array(f))

        a = np.array(self.all_distances())  # a: numpy array containing the attribute to be smoothed
        for i in range(iterations):
            a_prime = a + lamda * L * a
            a = a_prime
        # could fix boundaries by putting the corresponding columns of the sparse matrix to 0
        self.OVERWRITE_all_distances = a

    #############################
    #  ------ output
    def save_distances(self, name):
        utils.save_to_json(self.all_distances(), self.DATA_PATH, name)

    def save_distances_clusters(self, name):
        clusters_distances = {}
        for list_index in range(self.number_of_boundaries):
            clusters_distances[list_index] = []

        for i in range(self.VN):
            all_ds = self.all_clusters_distances(i)
            for j, d in enumerate(all_ds):
                clusters_distances[j].append(d)
        utils.save_to_json(clusters_distances, self.DATA_PATH, name)

    def save_start_vertices(self, name):
        utils.save_to_json([int(vi) for vi in self.all_target_vkeys], self.DATA_PATH, name)


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
