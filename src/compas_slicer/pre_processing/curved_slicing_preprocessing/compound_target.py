import numpy as np
import math
from compas.datastructures import Mesh
import compas_slicer.utilities as utils
import logging
import networkx as nx
from compas_slicer.slicers.slice_utilities import create_graph_from_mesh_vkeys
from compas_slicer.pre_processing.curved_slicing_preprocessing.geodesics import get_igl_EXACT_geodesic_distances

import statistics

logger = logging.getLogger('logger')

__all__ = ['CompoundTarget',
           'blend_union_list']


class CompoundTarget:
    """
    Represents a desired user-provided target. It acts as a key-frame that controls the print paths
    orientations. After the curved slicing , the print paths will be aligned to the compound target close to
    its area. The vertices that belong to the target are marked with their vertex attributes; they have
    data['v_attr'] = value.

    Attributes
    ----------
    mesh : :class:`compas.datastructures.Mesh`
    v_attr : str
        The key of the attribute dict to be checked.
    value : int
        The value of the attribute dict with key=v_attr. If in a vertex data[v_attr]==value then the vertex is part of
        this target.
    DATA_PATH : str
    has_blend_union: bool
    blend_radius : float
    geodesics_method : str
        'exact_igl'  exact igl geodesic distances
        'heat'   custom heat geodesic distances
    anisotropic_scaling : bool
        This is not yet implemented
    """

    def __init__(self, mesh, v_attr, value, DATA_PATH, has_blend_union=False, blend_radius=15.0,
                 geodesics_method='exact_igl', anisotropic_scaling=False):

        logger.info('Creating target with attribute : ' + v_attr + '=%d' % value)
        logger.info('has_blend_union : ' + str(has_blend_union) + ', blend_radius =  %.4f' % blend_radius)
        self.mesh = mesh
        self.v_attr = v_attr
        self.value = value
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)

        self.has_blend_union = has_blend_union
        self.blend_radius = blend_radius

        self.geodesics_method = geodesics_method
        self.anisotropic_scaling = anisotropic_scaling  # Anisotropic scaling not yet implemented

        self.offset = 0
        self.VN = len(list(self.mesh.vertices()))

        # filled in by function 'self.find_targets_connected_components()'
        self.all_target_vkeys = []  # flattened list with all vi_starts
        self.clustered_vkeys = []  # nested list with all vi_starts
        self.number_of_boundaries = None  # int

        self.weight_max_per_cluster = []

        # geodesic distances
        # filled in by function 'self.update_distances_lists()'
        self._distances_lists = []  # nested list. Shape: number_of_boundaries x number_of_vertices
        self._distances_lists_flipped = []  # nested list. Shape: number_of_vertices x number_of_boundaries
        self._np_distances_lists_flipped = np.array([])  # numpy array of self._distances_lists_flipped
        self._max_dist = None  # maximum get_distance value from the target on any vertex of the mesh

        # compute
        self.find_targets_connected_components()
        self.compute_geodesic_distances()

    #  --- Neighborhoods clustering
    def find_targets_connected_components(self):
        """
        Clusters all the vertices that belong to the target into neighborhoods using a graph.
        Each target can have an arbitrary number of neighborhoods/clusters.
        Fills in the attributes: self.all_target_vkeys, self.clustered_vkeys, self.number_of_boundaries
        """
        self.all_target_vkeys = [vkey for vkey, data in self.mesh.vertices(data=True) if
                                 data[self.v_attr] == self.value]
        assert len(self.all_target_vkeys) > 0, "There are no vertices in the mesh with the attribute : " \
                                               + self.v_attr + ", value : %d" % self.value
        G = create_graph_from_mesh_vkeys(self.mesh, self.all_target_vkeys)
        assert len(list(G.nodes())) == len(self.all_target_vkeys)
        self.number_of_boundaries = len(list(nx.connected_components(G)))

        for i, cp in enumerate(nx.connected_components(G)):
            self.clustered_vkeys.append(list(cp))
        logger.info("Compound target with 'boundary'=%d. Number of connected_components : %d" % (
            self.value, len(list(nx.connected_components(G)))))

    #  --- Geodesic distances
    def compute_geodesic_distances(self):
        """
        Computes the geodesic distances from each of the target's neighborhoods  to all the mesh vertices.
        Fills in the distances attributes.
        """
        if self.geodesics_method == 'exact_igl':
            distances_lists = [get_igl_EXACT_geodesic_distances(self.mesh, vstarts) for vstarts in
                               self.clustered_vkeys]
        elif self.geodesics_method == 'heat':
            raise NotImplementedError
        else:
            raise ValueError('Unknown geodesics method : ' + self.geodesics_method)

        distances_lists = [list(dl) for dl in distances_lists]  # number_of_boundaries x #V
        self.update_distances_lists(distances_lists)

    def update_distances_lists(self, distances_lists):
        """
        Fills in the distances attributes.
        """
        self._distances_lists = distances_lists
        self._distances_lists_flipped = []  # empty
        for i in range(self.VN):
            current_values = [self._distances_lists[list_index][i] for list_index in range(self.number_of_boundaries)]
            self._distances_lists_flipped.append(current_values)
        self._np_distances_lists_flipped = np.array(self._distances_lists_flipped)
        self._max_dist = np.max(self._np_distances_lists_flipped)

    #  --- Uneven weights
    @property
    def has_uneven_weights(self):
        """ Returns True if the target has uneven_weights calculated, False otherwise. """
        return len(self.weight_max_per_cluster) > 0

    def compute_uneven_boundaries_weight_max(self, other_target):
        """
        If the target has multiple neighborhoods/clusters of vertices, then it computes their maximum distance from
        the other_target. Based on that it calculates their weight_max for the interpolation process
        """
        if self.number_of_boundaries > 1:
            ds_avg_HIGH = self.get_boundaries_rel_dist_from_other_target(other_target)

            for i, d in enumerate(ds_avg_HIGH):  # offset all distances except the maximum one
                if abs(d - max(ds_avg_HIGH)) > 0.01:  # if it isn't weight the max value
                    ds_avg_HIGH[i] = d + self.offset

            self.weight_max_per_cluster = [d / max(ds_avg_HIGH) for d in ds_avg_HIGH]
            logger.info('weight_max_per_cluster : ' + str(self.weight_max_per_cluster))
        else:
            logger.info("Did not compute_norm_of_gradient uneven boundaries, target consists of single component")

    #  --- Relation to other target
    def get_boundaries_rel_dist_from_other_target(self, other_target, avg_type='median'):
        """
        Returns a list, one relative distance value per connected boundary neighborhood.
        That is the average of the distances of the vertices of that boundary neighborhood from the other_target.
        """
        distances = []
        for vi_starts in self.clustered_vkeys:
            ds = [other_target.get_distance(vi) for vi in vi_starts]
            if avg_type == 'mean':
                distances.append(statistics.mean(ds))
            else:  # 'median'
                distances.append(statistics.median(ds))
        return distances

    def get_extreme_distances_from_other_target(self, other_target):
        """
        Returns the minimum and maximum distance of the vertices of this target from the other_target
        """
        extreme_distances = []
        for v_index in other_target.all_target_vkeys:
            extreme_distances.append(self.get_all_distances()[v_index])
        return min(extreme_distances), max(extreme_distances)

    #############################
    #  --- get distances

    def get_all_clusters_distances(self, i):
        """ Returns distances from each cluster separately per vertex. Smooth union doesn't play play any role! """
        return [self._distances_lists[list_index][i] for list_index in range(self.number_of_boundaries)]

    def get_all_distances(self):
        """ Returns the resulting distances per every vertex. """
        return [self.get_distance(i) for i in range(self.VN)]

    def get_distance(self, i):
        """ Return get_distance for vertex with index i. """
        if self.has_blend_union:
            return self.blend_union(i)
        else:
            return self.union(i)

    def get_max_dist(self):
        """ Returns the maximum distance that the target has on a mesh vertex. """
        return self._max_dist

    def union(self, i):
        """ Union of distances for vertex with index i"""
        return np.min(self._np_distances_lists_flipped[i])

    def blend_union(self, i):
        """ Smooth union of distances for vertex with index i"""
        return blend_union_list(values=self._np_distances_lists_flipped[i], r=self.blend_radius)

    #############################
    #  --- scalar field smoothing

    def laplacian_smoothing(self, iterations, strength):
        """ Smooth the distances on the mesh, using iterative laplacian smoothing. """
        L = utils.get_mesh_laplacian_matrix_igl(self.mesh, fix_boundaries=True)
        new_distances_lists = []

        logger.info('Laplacian smoothing of all distances')
        for i, a in enumerate(self._distances_lists):
            a = np.array(a)  # a: numpy array containing the attribute to be smoothed
            for _ in range(iterations):  # iterative smoothing
                a_prime = a + strength * L * a
                a = a_prime
            new_distances_lists.append(list(a))
        self.update_distances_lists(new_distances_lists)

    #############################
    #  ------ output
    def save_distances(self, name):
        """
        Save distances to json.
        Saves one list with distance values (one per vertex).

        Parameters
        ----------
        name: str, name of json to be saved
        """
        utils.save_to_json(self.get_all_distances(), self.OUTPUT_PATH, name)

    def save_distances_clusters(self, name):
        """
        Save distances for each cluster separately to json.
        Saves a dict with (number_of_boundaries x VN) distance values.
            key: int, index of connected boundary neighborhood.
            value: list, distance values (one per vertex).

        Parameters
        ----------
        name: str, name of json to be saved
        """
        clusters_distances = {}
        for list_index in range(self.number_of_boundaries):
            clusters_distances[list_index] = []

        for i in range(self.VN):
            all_ds = self.get_all_clusters_distances(i)
            for j, d in enumerate(all_ds):
                clusters_distances[j].append(d)
        utils.save_to_json(clusters_distances, self.OUTPUT_PATH, name)

    #  ------ assign new Mesh
    def assign_new_mesh(self, mesh):
        """ When the base mesh changes, a new mesh needs to be assigned. """
        mesh.to_json(self.OUTPUT_PATH + "/temp.obj")
        mesh = Mesh.from_json(self.OUTPUT_PATH + "/temp.obj")
        self.mesh = mesh
        self.VN = len(list(self.mesh.vertices()))


####################
#  utils

def blend_union_list(values, r):
    """ Returns a smooth union of the elements of the list, with blend radius blend_radius. """
    d_result = 9999999  # very big number
    for d in values:
        d_result = blend_union(d_result, d, r)
    return d_result


def blend_union(da, db, r):
    """ Returns a smooth union of the two elements da, db with blend radius blend_radius. """
    e = max(r - abs(da - db), 0)
    return min(da, db) - e * e * 0.25 / r


def champfer_union(da, db, r):
    """ Returns a champfer union of the two elements da, db with blend radius blend_radius. """
    m = min(da, db)
    if m > (da ** 2 + db ** 2 - r ** 2) * math.sqrt(0.5):
        print('here')
    return min(m, (da ** 2 + db ** 2 - r ** 2) * math.sqrt(0.5))


if __name__ == "__main__":
    pass
