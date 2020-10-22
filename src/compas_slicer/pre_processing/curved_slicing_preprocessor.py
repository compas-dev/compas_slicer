import numpy as np
from compas_slicer.pre_processing import CompoundTarget
from compas_slicer.pre_processing import ScalarFieldEvaluation
import logging
import os
from compas.datastructures import Mesh
from compas_slicer.pre_processing import MeshSplitter, save_vertex_attributes, restore_mesh_attributes
import compas_slicer.utilities as utils

packages = utils.TerminalCommand('conda list').get_split_output_strings()
if 'igl' in packages:
    import igl

logger = logging.getLogger('logger')

__all__ = ['CurvedSlicingPreprocessor']

CUT_MESH = True
SEPARATE_NEIGHBORHOODS = True
TOPOLOGICAL_SORTING = True


class CurvedSlicingPreprocessor:
    def __init__(self, mesh, low_boundary_vs, high_boundary_vs, parameters, DATA_PATH):
        self.mesh = mesh
        self.parameters = parameters
        self.DATA_PATH = DATA_PATH
        self.target_LOW = None
        self.target_HIGH = None
        self.sf_evaluation = None

        self.mesh.update_default_vertex_attributes({'boundary': 0})
        for vkey, data in self.mesh.vertices(data=True):
            if vkey in low_boundary_vs:
                data['boundary'] = 1
            elif vkey in high_boundary_vs:
                data['boundary'] = 2

        self.split_meshes = []

    ###########################
    # --- General functionality

    def create_compound_targets(self):
        is_smooth, r = self.parameters['target_LOW_smooth'][0], self.parameters['target_LOW_smooth'][1]
        self.target_LOW = CompoundTarget(self.mesh, 'boundary', 1, self.DATA_PATH, is_smooth=is_smooth, r=r)
        is_smooth, r = self.parameters['target_HIGH_smooth'][0], self.parameters['target_HIGH_smooth'][1]
        self.target_HIGH = CompoundTarget(self.mesh, 'boundary', 2, self.DATA_PATH, is_smooth=is_smooth, r=r)
        self.target_HIGH.compute_uneven_boundaries_t_ends(self.target_LOW)
        #  --- save intermediary distance outputs
        if self.parameters['create_intermediary_outputs']:
            self.target_LOW.save_distances("distances_LOW.json")
            self.target_HIGH.save_distances("distances_HIGH.json")
            self.target_HIGH.save_distances_clusters("distances_clusters_HIGH.json")
            utils.save_to_json(self.target_HIGH.t_end_per_cluster, self.DATA_PATH, "t_end_per_cluster_HIGH.json")

    def scalar_field_evaluation(self):
        self.sf_evaluation = ScalarFieldEvaluation(self.mesh, self.target_LOW, self.target_HIGH)
        self.sf_evaluation.compute_norm_of_gradient()
        if self.parameters['create_intermediary_outputs']:
            utils.save_to_json(self.sf_evaluation.vertex_scalars_flattened, self.DATA_PATH, 'gradient_norm.json')

    def find_critical_points(self):
        self.sf_evaluation.find_critical_points()
        if self.parameters['create_intermediary_outputs']:
            utils.save_to_json(self.sf_evaluation.minima, self.DATA_PATH, "minima.json")
            utils.save_to_json(self.sf_evaluation.maxima, self.DATA_PATH, "maxima.json")
            utils.save_to_json(self.sf_evaluation.saddles, self.DATA_PATH, "saddles.json")

    ###########################
    # --- Region Split

    def region_split(self):
        print("")
        logging.info("--- Mesh region splitting")
        if len(self.sf_evaluation.saddles) == 0:
            logger.warning('There are no saddle points on the scalar field of the mesh.')
            return

        # if CUT_MESH:
        #     self.mesh.update_default_vertex_attributes({'cut': 0})
        #     region_split = MeshSplitter(self.mesh, self.target_LOW, self.target_HIGH, self.sf_evaluation.saddles,
        #                                 self.parameters, self.DATA_PATH)
        #     region_split.run()
        #
        #     self.mesh = region_split.mesh
        #     logger.info('Completed Region splitting')
        #     logger.info("Region split cut indices: " + str(region_split.cut_indices))
        #     if self.parameters['create_intermediary_outputs']:
        #         self.mesh.to_obj(os.path.join(self.DATA_PATH, 'resulting_split_mesh.obj'))
        #         self.mesh.to_json(os.path.join(self.DATA_PATH, 'resulting_split_mesh.json'))
        #         logger.info("Saving to Obj and Json: " + os.path.join(self.DATA_PATH, 'resulting_split_mesh.json'))
        #     utils.interrupt()

        if SEPARATE_NEIGHBORHOODS:
            print("")
            logger.info("--- Separating mesh disconnected components")
            self.mesh = Mesh.from_json(os.path.join(self.DATA_PATH, 'resulting_split_mesh.json'))
            region_split_cut_indices = get_existing_cut_indices(self.mesh)

            if self.parameters['create_intermediary_outputs']:
                utils.save_to_json(get_vertices_that_belong_to_cuts(self.mesh, region_split_cut_indices),
                                   self.DATA_PATH, "vertices_on_cuts.json")

            self.split_meshes = separate_disconnected_components_on_attribute(self.mesh, attr='cut',
                                                                              values=region_split_cut_indices,
                                                                              DATA_PATH=self.DATA_PATH)
            logger.info('Created %d split meshes.' % len(self.split_meshes))

        # if TOPOLOGICAL_SORTING:
        #     print("")
        #     logger.info("--- Topological sort of meshes directed graph to determine print order")
        #     graph = topo_sort.MeshDirectedGraph(self.final_meshes)
        #     all_orders = graph.get_all_topological_orders()
        #     print(all_orders)
        #     selected_order = all_orders[0]
        #     logger.info('selected_order : ' + str(selected_order))
        #     self.cleanup_mesh_attributes_based_on_selected_order(selected_order, graph)
        #
        #

        ### --- save final meshes
        print("")
        logger.info("--- Saving resulting split meshes")
        for i, m in enumerate(self.split_meshes):
            m.to_obj(os.path.join(self.DATA_PATH, 'split_mesh_' + str(i) + '.obj'))
            m.to_json(os.path.join(self.DATA_PATH, 'split_mesh_' + str(i) + '.json'))
        logger.info('Saving to Obj and Json: ' + os.path.join(self.DATA_PATH, 'split_mesh_%.obj'))
        logger.info("Saved %d split_meshes" % len(self.split_meshes))

        # def cleanup_mesh_attributes_based_on_selected_order(self, selected_order, graph):
        #     for index in selected_order:
        #         mesh = self.final_meshes[index]
        #         for child_node in graph.adj_list[index]:
        #             child_mesh = self.final_meshes[child_node]
        #             edge = graph.G.edges[index, child_node]
        #             cut_id = edge['cut']
        #             utils.replace_mesh_vertex_attribute(mesh, 'cut', cut_id, 'boundary', 2)
        #             utils.replace_mesh_vertex_attribute(child_mesh, 'cut', cut_id, 'boundary', 1)
        #
        #         # pts1 = utils.get_mesh_vertex_coords_with_attribute(mesh, 'boundary', 1)
        #         # pts2 = utils.get_mesh_vertex_coords_with_attribute(mesh, 'boundary', 2)
        #         # utils.save_json(utils.point_list_to_dict(pts1), self.DATA_PATH, 'pts_b_%d_1.json' % index)
        #         # utils.save_json(utils.point_list_to_dict(pts2), self.DATA_PATH, 'pts_b_%d_2.json' % index)


####################
# --- helpers


def separate_disconnected_components_on_attribute(mesh, attr, values, DATA_PATH):
    v_attributes_dict = save_vertex_attributes(mesh)

    # ## convert to np array for igl
    # v = np.array(mesh.vertices_attributes('xyz'))
    # v = v.reshape(-1, 3)  # vertices numpy array : #Vx3
    # key_index = mesh.key_index()
    # f = [[key_index[key] for key in mesh.face_vertices(fkey)] for fkey in mesh.faces()]
    # f = np.array(f)
    # f.reshape(-1, 3)  # faces numpy array : #Fx3)

    v, f = mesh.to_vertices_and_faces()
    v, f = np.array(v), np.array(f)

    ## create cut flags for igl
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

    ## cut mesh
    v_cut, f_cut = igl.cut_mesh(v, f, cut_flags)
    connected_components = igl.face_components(f_cut)

    f_dict = {}
    for i in range(max(connected_components) + 1):
        f_dict[i] = []
    for f_index, f in enumerate(f_cut):
        component = connected_components[f_index]
        f_dict[component].append(f)

    ## cut mesh
    cut_meshes = []
    for component in f_dict:
        cut_mesh = Mesh.from_vertices_and_faces(v_cut, f_dict[component])
        cut_mesh.cull_vertices()
        if len(list(cut_mesh.faces())) > 2:
            cut_mesh.to_obj(os.path.join(DATA_PATH, 'temp.obj'))
            cut_mesh = Mesh.from_obj(os.path.join(DATA_PATH, 'temp.obj'))  # get rid of too many empty keys
            cut_meshes.append(cut_mesh)

    for mesh in cut_meshes:
        restore_mesh_attributes(mesh, v_attributes_dict)

    return cut_meshes


def get_existing_cut_indices(mesh):
    cut_indices = []
    for vkey, data in mesh.vertices(data=True):
        if data['cut'] > 0:
            if data['cut'] not in cut_indices:
                cut_indices.append(data['cut'])
    cut_indices = sorted(cut_indices)
    return cut_indices


def get_vertices_that_belong_to_cuts(mesh, cut_indices):
    cuts_dict = {i: [] for i in cut_indices}

    for vkey, data in mesh.vertices(data=True):
        if data['cut'] > 0:
            cut_index = data['cut']
            cuts_dict[cut_index].append(mesh.vertex_coordinates(vkey))

    for cut_index in cuts_dict:
        cuts_dict[cut_index] = utils.point_list_to_dict(cuts_dict[cut_index])

    return cuts_dict
