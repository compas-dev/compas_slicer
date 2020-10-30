from compas_slicer.pre_processing import CompoundTarget
from compas_slicer.pre_processing import ScalarFieldEvaluation
import logging
import os
from compas.datastructures import Mesh
from compas_slicer.pre_processing.curved_slicing_preprocessing import mesh_region_split as rs
from compas_slicer.pre_processing import get_existing_cut_indices, get_vertices_that_belong_to_cuts, \
    replace_mesh_vertex_attribute
import compas_slicer.utilities as utils
from compas_slicer.print_organization.curved_print_organization import topological_sorting as topo_sort

logger = logging.getLogger('logger')

__all__ = ['CurvedSlicingPreprocessor']

CUT_MESH = True
SEPARATE_NEIGHBORHOODS = True
TOPOLOGICAL_SORTING = True


class CurvedSlicingPreprocessor:
    def __init__(self, mesh, parameters, DATA_PATH):
        self.mesh = mesh
        self.parameters = parameters
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
        self.target_LOW = None
        self.target_HIGH = None
        self.sf_evaluation = None

        self.split_meshes = []

    ###########################
    # --- General functionality

    def create_compound_targets(self):
        self.target_LOW = CompoundTarget(self.mesh, 'boundary', 1, self.DATA_PATH)
        self.target_HIGH = CompoundTarget(self.mesh, 'boundary', 2, self.DATA_PATH)
        self.target_HIGH.compute_uneven_boundaries_t_ends(self.target_LOW)
        #  --- save intermediary distance outputs
        if self.parameters['create_intermediary_outputs']:
            self.target_LOW.save_distances("distances_LOW.json")
            self.target_HIGH.save_distances("distances_HIGH.json")
            self.target_HIGH.save_distances_clusters("distances_clusters_HIGH.json")
            utils.save_to_json(self.target_HIGH.t_end_per_cluster, self.OUTPUT_PATH, "t_end_per_cluster_HIGH.json")

    def scalar_field_evaluation(self, output_filename):
        """
        Creates a ScalarFieldEvaluation that is saved in self.sf_evaluation
        Computes the gradient norm
        Saves it to Json on the output_filename
        """
        self.sf_evaluation = ScalarFieldEvaluation(self.mesh, self.target_LOW, self.target_HIGH)
        self.sf_evaluation.compute_norm_of_gradient()
        if self.parameters['create_intermediary_outputs']:
            utils.save_to_json(self.sf_evaluation.vertex_scalars_flattened, self.OUTPUT_PATH, output_filename)

    def find_critical_points(self, output_filenames):
        self.sf_evaluation.find_critical_points()
        if self.parameters['create_intermediary_outputs']:
            utils.save_to_json(self.sf_evaluation.minima, self.OUTPUT_PATH, output_filenames[0])
            utils.save_to_json(self.sf_evaluation.maxima, self.OUTPUT_PATH, output_filenames[1])
            utils.save_to_json(self.sf_evaluation.saddles, self.OUTPUT_PATH, output_filenames[2])

    ###########################
    # --- Region Split

    def region_split(self, save_split_meshes):
        print("")
        logging.info("--- Mesh region splitting")
        if len(self.sf_evaluation.saddles) == 0:
            logger.warning('There are no saddle points on the scalar field of the mesh.')
            return

        if CUT_MESH:
            self.mesh.update_default_vertex_attributes({'cut': 0})
            mesh_splitter = rs.MeshSplitter(self.mesh, self.target_LOW, self.target_HIGH, self.sf_evaluation.saddles,
                                            self.parameters, self.DATA_PATH)
            mesh_splitter.run()

            self.mesh = mesh_splitter.mesh
            logger.info('Completed Region splitting')
            logger.info("Region split cut indices: " + str(mesh_splitter.cut_indices))
            if self.parameters['create_intermediary_outputs']:
                self.mesh.to_obj(os.path.join(self.OUTPUT_PATH, 'mesh_with_cuts.obj'))
                self.mesh.to_json(os.path.join(self.OUTPUT_PATH, 'mesh_with_cuts.json'))
                logger.info("Saving to Obj and Json: " + os.path.join(self.OUTPUT_PATH, 'mesh_with_cuts.json'))

        if SEPARATE_NEIGHBORHOODS:
            print("")
            logger.info("--- Separating mesh disconnected components")
            self.mesh = Mesh.from_json(os.path.join(self.OUTPUT_PATH, 'mesh_with_cuts.json'))
            region_split_cut_indices = get_existing_cut_indices(self.mesh)

            if self.parameters['create_intermediary_outputs']:
                utils.save_to_json(get_vertices_that_belong_to_cuts(self.mesh, region_split_cut_indices),
                                   self.OUTPUT_PATH, "vertices_on_cuts.json")

            self.split_meshes = rs.separate_disconnected_components(self.mesh, attr='cut',
                                                                    values=region_split_cut_indices,
                                                                    OUTPUT_PATH=self.OUTPUT_PATH)
            logger.info('Created %d split meshes.' % len(self.split_meshes))

        if TOPOLOGICAL_SORTING:
            print("")
            logger.info("--- Topological sort of meshes directed graph to determine print order")
            graph = topo_sort.MeshDirectedGraph(self.split_meshes)
            all_orders = graph.get_all_topological_orders()
            selected_order = all_orders[0]
            logger.info('selected_order : ' + str(selected_order))
            self.cleanup_mesh_attributes_based_on_selected_order(selected_order, graph)

            # reorder split_meshes based on selected order
            self.split_meshes = [self.split_meshes[i] for i in selected_order]

        # --- save split meshes
        if save_split_meshes:
            print("")
            logger.info("--- Saving resulting split meshes")
            for i, m in enumerate(self.split_meshes):
                m.to_obj(os.path.join(self.OUTPUT_PATH, 'split_mesh_' + str(i) + '.obj'))
                m.to_json(os.path.join(self.OUTPUT_PATH, 'split_mesh_' + str(i) + '.json'))
            logger.info('Saving to Obj and Json: ' + os.path.join(self.OUTPUT_PATH, 'split_mesh_%.obj'))
            logger.info("Saved %d split_meshes" % len(self.split_meshes))
            print('')

    def cleanup_mesh_attributes_based_on_selected_order(self, selected_order, graph):
        for index in selected_order:
            mesh = self.split_meshes[index]
            for child_node in graph.adj_list[index]:
                child_mesh = self.split_meshes[child_node]
                edge = graph.G.edges[index, child_node]
                cut_id = edge['cut']
                replace_mesh_vertex_attribute(mesh, 'cut', cut_id, 'boundary', 2)
                replace_mesh_vertex_attribute(child_mesh, 'cut', cut_id, 'boundary', 1)

            if self.parameters['create_intermediary_outputs']:
                pts_boundary_LOW = utils.get_mesh_vertex_coords_with_attribute(mesh, 'boundary', 1)
                pts_boundary_HIGH = utils.get_mesh_vertex_coords_with_attribute(mesh, 'boundary', 2)
                utils.save_to_json(utils.point_list_to_dict(pts_boundary_LOW), self.OUTPUT_PATH,
                                   'pts_boundary_LOW_%d.json' % index)
                utils.save_to_json(utils.point_list_to_dict(pts_boundary_HIGH), self.OUTPUT_PATH,
                                   'pts_boundary_HIGH_%d.json' % index)
