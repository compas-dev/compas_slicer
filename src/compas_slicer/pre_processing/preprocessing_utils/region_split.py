import os
import logging
import numpy as np
import copy
import compas
import compas_slicer.utilities as utils
from compas_slicer.pre_processing.preprocessing_utils import restore_mesh_attributes, save_vertex_attributes
from compas.datastructures import Mesh
from compas_slicer.pre_processing.preprocessing_utils import assign_interpolation_distance_to_mesh_vertex
from compas_slicer.slicers.slice_utilities import ScalarFieldContours
from compas_slicer.pre_processing.preprocessing_utils import assign_interpolation_distance_to_mesh_vertices
from compas_slicer.pre_processing.gradient_evaluation import GradientEvaluation
from compas.geometry import Line, distance_point_point_sqrd, project_point_line

packages = utils.TerminalCommand('conda list').get_split_output_strings()
if 'igl' in packages:
    import igl

logger = logging.getLogger('logger')

__all__ = ['MeshSplitter']

# --- Parameters
T_SEARCH_RESOLUTION = 60000
HIT_THRESHOLD = 0.02


class MeshSplitter:
    """
    Curved slicing pre-processing step.

    Takes one continuous mesh with various saddle points and splits it up
    at every saddle point following the direction of the iso-contour that intersects that saddle point,
    so that the resulting mesh has no remaining saddle points.

    The result is a series of split meshes whose vertex attributes have been updated with boundary attributes at the
    newly created cuts, (i.e. they all have vertex 'boundary' attributes 1,2 on their lower and upper
    boundaries)

    For each newly created mesh, a separate slicer needs to be created. Like that,
    we will always have one slicer per mesh with the correct attributes already assigned.
    However, it can still happen that a slicer that takes a split mesh outputs more than one
    vertical_layers_print_data (vertical layers).

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    target_LOW: :class: 'compas_slicer.pre_processing.CompoundTarget'
    target_HIGH: :class: 'compas_slicer.pre_processing.CompoundTarget'
    DATA_PATH: str, the path to the data folder
    """

    def __init__(self, mesh, target_LOW, target_HIGH, DATA_PATH):
        self.mesh = mesh  # compas mesh
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
        self.target_LOW, self.target_HIGH = target_LOW, target_HIGH

        assign_interpolation_distance_to_mesh_vertices(self.mesh, weight=0.5, target_LOW=self.target_LOW,
                                                       target_HIGH=self.target_HIGH)
        g_evaluation = GradientEvaluation(self.mesh, self.DATA_PATH)
        g_evaluation.find_critical_points()  # First estimation of saddle points with weight = 0.5
        self.saddles = g_evaluation.saddles
        self.cut_indices = []

    # --------------------------- main
    def run(self):
        """
        Runs the mesh splitting process. This consists of the following parts.

        (1) Find the iso-contours that intersect the saddle points.
        Iteratively find the weights (from 0 to 1) that output a distance field whose iso-contour is intersecting
        each saddle point. Here two iterations are carried out (one rough and one exact search).

        For each saddle point and its respective weight and iso-contour:
        (2) Find the zero-crossing points of the iso-contour and merge points that are close to the saddle to ensure
        connection.
        (3) Cleanup iso-contour. Only keep neighborhoods that are intersecting the saddle point. Discard all other.
        (4) Create the cut on the mesh.
        (5) Weld the resulting mesh, and restore all the vertex attributes. Note that the mesh remains in one piece,
        although the cuts have been created.
        (6) Update compound tardets with the new mesh.
        """

        # (1) first rough estimation of split params
        split_params = self.identify_positions_to_split(self.saddles)
        # TODO: merge params that are too close together to avoid creation of very thin neighborhoods.
        logger.info("%d Split params. First rough estimation :  " % len(split_params) + str(split_params))

        # split mesh at params
        logger.info('Splitting mesh at split params')
        current_cut_index = 1

        for i, param_first_estimation in enumerate(split_params):
            print('')
            logger.info('cut_index : %d, param_first_estimation : %.6f' % (current_cut_index, param_first_estimation))

            # --- (1) More exact estimation of intersecting weight. Recompute gradient evaluation.
            # Find exact saddle point and the weight that intersects it.

            assign_interpolation_distance_to_mesh_vertices(self.mesh, weight=param_first_estimation,
                                                           target_LOW=self.target_LOW, target_HIGH=self.target_HIGH)
            g_evaluation = GradientEvaluation(self.mesh, self.DATA_PATH)
            g_evaluation.find_critical_points()
            saddles_ds_tupples = [(vkey, abs(g_evaluation.mesh.vertex_attribute(vkey, 'scalar_field'))) for vkey in
                                  g_evaluation.saddles]
            saddles_ds_tupples = sorted(saddles_ds_tupples, key=lambda saddle_tupple: saddle_tupple[1])
            vkey = saddles_ds_tupples[0][0]
            t = self.identify_positions_to_split([vkey])[0]
            logger.info('vkey_exact : %d , t_exact : %.6f' % (vkey, t))

            # --- (2) find zero-crossing points
            assign_interpolation_distance_to_mesh_vertices(self.mesh, t, self.target_LOW, self.target_HIGH)
            zero_contours = ScalarFieldContours(self.mesh)
            zero_contours.compute()
            keys_of_clusters_to_keep = merge_clusters_saddle_point(zero_contours, saddle_vkeys=[vkey])

            # --- (3) Cleaning up zero-crossing neighborhoods
            cleanup_unrelated_isocontour_neighborhoods(zero_contours, keys_of_clusters_to_keep)

            if zero_contours:  # if there are remaining zero-crossing neighborhoods
                zero_contours = smoothen_cut(zero_contours, self.mesh, saddle_vkeys=[vkey], iterations=15,
                                             strength=0.2)  # smoothen the cut close to the saddle point.

                # save to json intermediary results
                zero_contours.save_point_clusters_as_polylines_to_json(self.OUTPUT_PATH,
                                                                       'point_clusters_polylines_%d.json' % int(i))

                #  --- (4) Create cut
                logger.info("Creating cut on mesh")
                self.cut_indices.append(current_cut_index)
                self.split_intersected_faces(zero_contours, current_cut_index)
                current_cut_index += 1

                #  --- (5) Weld mesh and restore attributes
                logger.info('Cleaning up the mesh. Welding and restoring attributes')
                v_attributes_dict = save_vertex_attributes(self.mesh)
                self.mesh = weld_mesh(self.mesh, self.OUTPUT_PATH)
                restore_mesh_attributes(self.mesh, v_attributes_dict)

                #  --- (6) Update targets
                if i < len(split_params) - 1:  # does not need to happen at the end
                    logger.info('Updating targets, recomputing geodesic distances')
                    self.update_targets()

            self.mesh.to_obj(os.path.join(self.OUTPUT_PATH, 'most_recent_cut_mesh.obj'))

    def update_targets(self):
        """
        Update targets with the new mesh that was created during the split process.
        Note: This only works if the target vertices have not been touched. If all has gone well, targets can only have
        minima and maxima, so they should remain intact after the split
        """
        self.target_LOW.assign_new_mesh(self.mesh)
        self.target_LOW.find_targets_connected_components()
        self.target_LOW.compute_geodesic_distances()
        if self.target_HIGH:
            self.target_HIGH.assign_new_mesh(self.mesh)
            self.target_HIGH.find_targets_connected_components()
            self.target_HIGH.compute_geodesic_distances()

    def split_intersected_faces(self, zero_contours, cut_index):
        """
        Create cuts on intersected faces

        Parameters
        ----------
        zero_contours: :class: 'compas_slicer.pre_processing.ScalarFieldContours'
        cut_index: int, the vertex attribute value data['cut'] of the current cut
        """
        for key in zero_contours.sorted_point_clusters:  # cluster_pair
            edges = zero_contours.sorted_edge_clusters[key]
            pts = zero_contours.sorted_point_clusters[key]

            # add first vertex
            p = pts[0]
            v0 = self.mesh.add_vertex(x=p[0], y=p[1], z=p[2], attr_dict={'cut': 1})

            for i, edge in enumerate(edges):
                next_edge = edges[(i + 1) % len(edges)]
                p = pts[(i + 1) % len(pts)]

                faces_current_edge = self.mesh.edge_faces(u=edge[0], v=edge[1])
                faces_next_edge = self.mesh.edge_faces(u=next_edge[0], v=next_edge[1])

                fkey_common = list(set(faces_current_edge).intersection(faces_next_edge))[0]
                vkey_common = list(set(edge).intersection(next_edge))[0]
                v_other_a = list(set(edge).difference([vkey_common]))[0]
                v_other_b = list(set(next_edge).difference([vkey_common]))[0]

                v_new = self.mesh.add_vertex(x=p[0], y=p[1], z=p[2], attr_dict={'cut': cut_index})

                # remove and add faces
                if fkey_common in list(self.mesh.faces()):
                    self.mesh.delete_face(fkey_common)
                    self.mesh.add_face([vkey_common, v_new, v0])
                    self.mesh.add_face([v_new, v_other_a, v0])
                    self.mesh.add_face([v_other_b, v_other_a, v_new])
                else:
                    logger.warning('Did not need to modify faces.')
                v0 = v_new

        self.mesh.cull_vertices()  # remove all unused vertices
        try:
            self.mesh.unify_cycles()
        except AssertionError:
            logger.warning('Could NOT unify cycles')
        if not self.mesh.is_valid():
            logger.warning('Attention! Mesh is NOT valid!')

    def identify_positions_to_split(self, saddles):
        """
        Find the weights that create iso-contours that intersect the saddle points.

        Parameters
        ----------
        saddles: list, int, the vertex keys of the saddle points

        Returns
        ----------
        list, float, the weights from 0 to 1. One for each saddle point.
        """
        split_params = []
        for vkey in saddles:
            param = self.find_weight_intersecting_vkey(vkey, threshold=HIT_THRESHOLD, resolution=T_SEARCH_RESOLUTION)
            split_params.append(param)
        return split_params

    def find_weight_intersecting_vkey(self, vkey, threshold, resolution):
        """
        Find the weights that intersect the vertex.

        Parameters
        ----------
        vkey: list, int, the vertex key to intersect
        threshold: float, the d value below which we consider we have a hit. Should be a very small value
        resolution: int, the resolution of search, should be a value more than 10**4

        Returns
        ----------
        float, the weights from 0 to 1.
        """
        weight_list = get_weights_list(n=resolution, start=0.001, end=0.999)
        # TODO: save next d to avoid re-evaluating
        for i, weight in enumerate(weight_list[:-1]):
            current_d = assign_interpolation_distance_to_mesh_vertex(vkey, weight, self.target_LOW, self.target_HIGH)
            next_d = assign_interpolation_distance_to_mesh_vertex(vkey, weight_list[i + 1], self.target_LOW, self.target_HIGH)
            if abs(current_d) < abs(next_d) and current_d < threshold:
                return weight
        raise ValueError('Could NOT find param for saddle vkey %d!' % vkey)


###############################################
# --- helpers
###############################################

def get_weights_list(n, start=0.03, end=1.0):
    """ Returns a numpy array with n numbers from start to end. """
    return list(np.arange(start=start, stop=end, step=(end - start) / n))


###############################################
# --- Separate disconnected components

def separate_disconnected_components(mesh, attr, values, OUTPUT_PATH):
    """
    Given a mesh with cuts that have already been created, it separates the disconnected
    components using the igl function. Then it welds them and restores their attributes.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    attr: str, the key of the vertex attributes that signals the cuts. most likely 'cut'
    values: list, int, the cut indices
    OUTPUT_PATH: str, the path to the output folder

    Returns
    ----------
    list, :class: 'compas.datastructures.Mesh' The resulting split meshes.
    """

    v_attributes_dict = save_vertex_attributes(mesh)

    v, f = mesh.to_vertices_and_faces()
    v, f = np.array(v), np.array(f)

    # --- create cut flags for igl
    cut_flags = []
    for fkey in mesh.faces():
        edges = mesh.face_halfedges(fkey)
        current_face_flags = []
        for fu, fv in edges:
            fu_attr, fv_attr = mesh.vertex_attribute(fu, attr), mesh.vertex_attribute(fv, attr)
            if fu_attr == fv_attr and fu_attr in values:
                current_face_flags.append(1)
            else:
                current_face_flags.append(0)
        cut_flags.append(current_face_flags)
    cut_flags = np.array(cut_flags)
    assert cut_flags.shape == f.shape

    # --- cut mesh
    v_cut, f_cut = igl.cut_mesh(v, f, cut_flags)
    connected_components = igl.face_components(f_cut)

    f_dict = {}
    for i in range(max(connected_components) + 1):
        f_dict[i] = []
    for f_index, f in enumerate(f_cut):
        component = connected_components[f_index]
        f_dict[component].append(f)

    cut_meshes = []
    for component in f_dict:
        cut_mesh = Mesh.from_vertices_and_faces(v_cut, f_dict[component])
        cut_mesh.cull_vertices()
        if len(list(cut_mesh.faces())) > 2:
            cut_mesh.to_obj(os.path.join(OUTPUT_PATH, 'temp.obj'))
            cut_mesh = Mesh.from_obj(os.path.join(OUTPUT_PATH, 'temp.obj'))  # get rid of too many empty keys
            cut_meshes.append(cut_mesh)

    for mesh in cut_meshes:
        restore_mesh_attributes(mesh, v_attributes_dict)

    return cut_meshes


###############################################
# --- saddle points merging


def smoothen_cut(zero_contours, mesh, saddle_vkeys, iterations, strength, distance_threshold=20.0*20.0):
    """ Iterative smoothing of the cut around the saddle point. """
    for _ in range(iterations):
        saddles = [mesh.vertex_coordinates(key) for key in saddle_vkeys]
        count = 0

        for cluster_key in zero_contours.sorted_point_clusters:
            pts = zero_contours.sorted_point_clusters[cluster_key]
            edges = zero_contours.sorted_edge_clusters[cluster_key]
            for i, pt in enumerate(pts):
                if 0.01 < min([distance_point_point_sqrd(pt, s) for s in saddles]) < distance_threshold:
                    count += 1
                    edge = edges[i]
                    prev = pts[i - 1]
                    next_p = pts[(i + 1) % len(pts)]
                    avg = [(prev[0] + next_p[0]) * 0.5, (prev[1] + next_p[1]) * 0.5, (prev[2] + next_p[2]) * 0.5]
                    point = np.array(avg) * strength + np.array(pt) * (1 - strength)
                    line = Line(mesh.vertex_coordinates(edge[0]), mesh.vertex_coordinates(edge[1]))
                    projected_pt = project_point_line(point, line)
                    pts[i] = projected_pt
                    zero_contours.sorted_point_clusters[cluster_key][i] = projected_pt

    return zero_contours


def merge_clusters_saddle_point(zero_contours, saddle_vkeys):
    """
    Merge the points that are on edges that have the saddle point as one of their edges to the saddle point.

    Parameters
    ----------
    zero_contours: :class: 'compas_slicer.pre_processing.ScalarFieldContours'
    saddle_vkeys: list, int, the vertex keys of the current saddle points.
    (Currently this can only be a single saddle point)

    Returns
    ----------
    list, int. The index neighborhoods that are related to the saddle points.
    """
    keys_of_clusters_to_keep = []
    for cluster_key in zero_contours.sorted_edge_clusters:
        edges = zero_contours.sorted_edge_clusters[cluster_key]
        for i, e in enumerate(edges):
            for saddle_vkey in saddle_vkeys:
                if saddle_vkey in e:
                    zero_contours.sorted_point_clusters[cluster_key][i] = \
                        zero_contours.mesh.vertex_coordinates(saddle_vkey)  # merge point with saddle point
                    print('Found edge to merge: ' + str(e))
                    if cluster_key not in keys_of_clusters_to_keep:
                        keys_of_clusters_to_keep.append(cluster_key)

    return keys_of_clusters_to_keep


def cleanup_unrelated_isocontour_neighborhoods(zero_contours, keys_of_clusters_to_keep):
    """
    Remove the neighborhoods of the zero-crossing contour when they are not related to the saddle points.

    Parameters
    ----------
    zero_contours: :class: 'compas_slicer.pre_processing.ScalarFieldContours'
    keys_of_clusters_to_keep: list, int. The index neighborhoods that are related to the saddle points.
    """
    if len(keys_of_clusters_to_keep) == 0:
        logger.error("No common vertex found! Skipping this split_param")
        return None
    else:
        logger.info('keys_of_clusters_to_keep : ' + str(keys_of_clusters_to_keep))
        # empty all other clusters that are not in the matching_pair
        sorted_point_clusters_clean = copy.deepcopy(zero_contours.sorted_point_clusters)
        sorted_edge_clusters_clean = copy.deepcopy(zero_contours.sorted_edge_clusters)
        for key in zero_contours.sorted_point_clusters:
            if key not in keys_of_clusters_to_keep:
                del sorted_point_clusters_clean[key]
                del sorted_edge_clusters_clean[key]

        zero_contours.sorted_point_clusters = sorted_point_clusters_clean
        zero_contours.sorted_edge_clusters = sorted_edge_clusters_clean


########################################################
# --- Mesh welding and sanitizing

def weld_mesh(mesh, OUTPUT_PATH, precision='2f'):
    """ Welds mesh and check that the result is valid. """
    for f_key in mesh.faces():
        if len(mesh.face_vertices(f_key)) < 3:
            mesh.delete_face(f_key)

    welded_mesh = compas.datastructures.mesh_weld(mesh, precision=precision)

    welded_mesh.to_obj(os.path.join(OUTPUT_PATH, 'temp.obj'))  # make sure there's no empty f_keys
    welded_mesh = Mesh.from_obj(os.path.join(OUTPUT_PATH, 'temp.obj'))  # TODO: find a better way to do this

    try:
        welded_mesh.unify_cycles()
        logger.info("Unified cycles of welded_mesh")
    except AssertionError:
        logger.error("Attention! Could NOT unify cycles of welded_mesh")

    if not welded_mesh.is_valid():  # and iteration < 3:
        logger.error("Attention! Welded mesh is INVALID")
    if not welded_mesh.is_manifold():
        logger.error("Attention! Welded mesh is NON-MANIFOLD")

    return welded_mesh


if __name__ == "__main__":
    pass
