from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from compas.datastructures import Mesh
from loguru import logger

import compas_slicer.utilities as utils
from compas_slicer.parameters import get_param
from compas_slicer.pre_processing.gradient_evaluation import GradientEvaluation
from compas_slicer.pre_processing.preprocessing_utils import assign_interpolation_distance_to_mesh_vertices
from compas_slicer.pre_processing.preprocessing_utils import region_split as rs
from compas_slicer.pre_processing.preprocessing_utils import topological_sorting as topo_sort
from compas_slicer.pre_processing.preprocessing_utils.compound_target import CompoundTarget
from compas_slicer.pre_processing.preprocessing_utils.mesh_attributes_handling import (
    get_existing_cut_indices,
    get_vertices_that_belong_to_cuts,
    replace_mesh_vertex_attribute,
)

if TYPE_CHECKING:
    from compas_slicer.pre_processing.preprocessing_utils.topological_sorting import MeshDirectedGraph


__all__ = ['InterpolationSlicingPreprocessor']


class InterpolationSlicingPreprocessor:
    """
    Takes care of all the pre-processing that is (or might be) needed before the interpolation slicing process.
    Not all the functionality needs to be run every time, depending on the characteristics of the inputs.

    Attributes
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
    parameters: dict
    DATA_PATH: str, path to the data folder
    """

    def __init__(self, mesh: Mesh, parameters: dict[str, Any], DATA_PATH: str | Path) -> None:
        self.mesh = mesh
        self.parameters = parameters
        self.DATA_PATH = DATA_PATH

        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
        self.target_LOW: CompoundTarget | None = None
        self.target_HIGH: CompoundTarget | None = None

        self.split_meshes: list[Mesh] = []
        # The meshes that result from the region splitting process.

        utils.utils.check_triangular_mesh(mesh)

    ###########################
    # --- compound targets

    def create_compound_targets(self) -> None:
        """ Creates the target_LOW and the target_HIGH and computes the geodesic distances. """

        # --- low target
        geodesics_method = get_param(self.parameters, key='target_LOW_geodesics_method',
                                     defaults_type='interpolation_slicing')
        method: str
        params: list[Any]
        method, params = 'min', []  # no other union methods currently supported for lower target
        self.target_LOW = CompoundTarget(self.mesh, 'boundary', 1, self.DATA_PATH,
                                         union_method=method,
                                         union_params=params,
                                         geodesics_method=geodesics_method)

        # --- high target
        geodesics_method = get_param(self.parameters, key='target_HIGH_geodesics_method',
                                     defaults_type='interpolation_slicing')
        method, params = get_union_method(self.parameters)
        logger.info("Creating target with union type : " + method + " and params : " + str(params))
        self.target_HIGH = CompoundTarget(self.mesh, 'boundary', 2, self.DATA_PATH,
                                          union_method=method,
                                          union_params=params,
                                          geodesics_method=geodesics_method)

        # --- uneven boundaries of high target
        self.target_HIGH.offset = get_param(self.parameters, key='uneven_upper_targets_offset',
                                            defaults_type='interpolation_slicing')
        self.target_HIGH.compute_uneven_boundaries_weight_max(self.target_LOW)

        #  --- save intermediary get_distance outputs
        self.target_LOW.save_distances("distances_LOW.json")
        self.target_HIGH.save_distances("distances_HIGH.json")

    def targets_laplacian_smoothing(self, iterations: int, strength: float) -> None:
        """
        Smooth geodesic distances of targets. Saves again the distances to json.

        Parameters
        ----------
        iterations: int
        strength: float
        """
        assert self.target_LOW is not None and self.target_HIGH is not None
        self.target_LOW.laplacian_smoothing(iterations=iterations, strength=strength)
        self.target_HIGH.laplacian_smoothing(iterations=iterations, strength=strength)
        self.target_LOW.save_distances("distances_LOW.json")
        self.target_HIGH.save_distances("distances_HIGH.json")

    ###########################
    # --- scalar field evaluation

    def create_gradient_evaluation(
        self,
        target_1: CompoundTarget,
        target_2: CompoundTarget | None = None,
        save_output: bool = True,
        norm_filename: str = 'gradient_norm.json',
        g_filename: str = 'gradient.json',
    ) -> GradientEvaluation:
        """
        Creates a compas_slicer.pre_processing.GradientEvaluation that is stored in self.g_evaluation
        Also, computes the gradient and gradient_norm and saves them to Json .
        """
        assert self.target_LOW is not None and self.target_HIGH is not None
        assert self.target_LOW.VN == target_1.VN, "Attention! Preprocessor does not match targets. "
        assign_interpolation_distance_to_mesh_vertices(self.mesh, weight=0.5,
                                                       target_LOW=self.target_LOW, target_HIGH=self.target_HIGH)
        g_evaluation = GradientEvaluation(self.mesh, self.DATA_PATH)
        g_evaluation.compute_gradient()
        g_evaluation.compute_gradient_norm()

        if save_output:
            # save results to json
            utils.save_to_json(g_evaluation.vertex_gradient_norm, self.OUTPUT_PATH, norm_filename)
            utils.save_to_json(utils.point_list_to_dict(g_evaluation.vertex_gradient), self.OUTPUT_PATH, g_filename)

        return g_evaluation

    def find_critical_points(
        self, g_evaluation: GradientEvaluation, output_filenames: tuple[str, str, str]
    ) -> None:
        """ Computes and saves to json the critical points of the df on the mesh (minima, maxima, saddles)"""
        g_evaluation.find_critical_points()
        # save results to json
        utils.save_to_json(g_evaluation.minima, self.OUTPUT_PATH, output_filenames[0])
        utils.save_to_json(g_evaluation.maxima, self.OUTPUT_PATH, output_filenames[1])
        utils.save_to_json(g_evaluation.saddles, self.OUTPUT_PATH, output_filenames[2])

    ###########################
    # --- Region Split

    def region_split(
        self,
        cut_mesh: bool = True,
        separate_neighborhoods: bool = True,
        topological_sorting: bool = True,
        save_split_meshes: bool = True,
    ) -> None:
        """
        Splits the mesh on the saddle points. This process can take a long time.
        It consists of four parts:
        1) Create cuts on the mesh so that they intersect the saddle points and follow the get_distance function
        iso-contour
        2) Separate mesh neighborhoods  from cuts
        3) Topological sorting of split meshes to determine their connectivity and sequence.
        4) Finally resulting meshes are saved to json.

        The intermediary outputs are saved to json, so if you don'weight want to be recomputing the entire thing every
        time, you can turn the respective processes to false.
        """

        logger.info("--- Mesh region splitting")

        if cut_mesh:  # (1)
            self.mesh.update_default_vertex_attributes({'cut': 0})
            mesh_splitter = rs.MeshSplitter(self.mesh, self.target_LOW, self.target_HIGH, self.DATA_PATH)
            mesh_splitter.run()

            self.mesh = mesh_splitter.mesh
            logger.info('Completed Region splitting')
            logger.info("Region split cut indices: " + str(mesh_splitter.cut_indices))
            # save results to json
            output_path = Path(self.OUTPUT_PATH)
            self.mesh.to_obj(str(output_path / 'mesh_with_cuts.obj'))
            self.mesh.to_json(str(output_path / 'mesh_with_cuts.json'))
            logger.info(f"Saving to Obj and Json: {output_path / 'mesh_with_cuts.json'}")

        if separate_neighborhoods:  # (2)
            logger.info("--- Separating mesh disconnected components")
            self.mesh = Mesh.from_json(str(Path(self.OUTPUT_PATH) / 'mesh_with_cuts.json'))
            region_split_cut_indices = get_existing_cut_indices(self.mesh)

            # save results to json
            utils.save_to_json(get_vertices_that_belong_to_cuts(self.mesh, region_split_cut_indices),
                               self.OUTPUT_PATH, "vertices_on_cuts.json")

            self.split_meshes = rs.separate_disconnected_components(self.mesh, attr='cut',
                                                                    values=region_split_cut_indices,
                                                                    OUTPUT_PATH=self.OUTPUT_PATH)
            logger.info(f'Created {len(self.split_meshes)} split meshes.')

        if topological_sorting:  # (3)
            logger.info("--- Topological sort of meshes directed graph to determine print order")
            graph = topo_sort.MeshDirectedGraph(self.split_meshes, self.DATA_PATH)
            all_orders = graph.get_all_topological_orders()
            selected_order = all_orders[0]
            logger.info('selected_order : ' + str(selected_order))  # TODO: improve the way an order is selected
            self.cleanup_mesh_attributes_based_on_selected_order(selected_order, graph)

            # reorder split_meshes based on selected order
            self.split_meshes = [self.split_meshes[i] for i in selected_order]

        # --- save split meshes
        if save_split_meshes:  # (4)
            logger.info("--- Saving resulting split meshes")
            output_path = Path(self.OUTPUT_PATH)
            for i, m in enumerate(self.split_meshes):
                m.to_obj(str(output_path / f'split_mesh_{i}.obj'))
                m.to_json(str(output_path / f'split_mesh_{i}.json'))
            logger.info(f'Saving to Obj and Json: {output_path / "split_mesh_%.obj"}')
            logger.info(f"Saved {len(self.split_meshes)} split_meshes")

    def cleanup_mesh_attributes_based_on_selected_order(
        self, selected_order: list[int], graph: MeshDirectedGraph
    ) -> None:
        """
        Based on the selected order of split meshes, it rearranges their attributes, so that they can then be used
        with an interpolation slicer that requires data['boundary'] to be filled for every vertex.
        The vertices that originated from cuts have data['cut']=cut_index. This is replaced
        by data['boundary'] = 1 or 2 depending on connectivity of mesh.

        Parameters
        ----------
        selected_order: list, int
            The indices of ordered split meshes.
        graph: :class: 'networkx.Graph'
        """
        for index in selected_order:
            mesh = self.split_meshes[index]
            for child_node in graph.adj_list[index]:
                child_mesh = self.split_meshes[child_node]
                edge = graph.G.edges[index, child_node]
                common_cuts = edge['cut']
                for cut_id in common_cuts:
                    replace_mesh_vertex_attribute(mesh, 'cut', cut_id, 'boundary', 2)
                    replace_mesh_vertex_attribute(child_mesh, 'cut', cut_id, 'boundary', 1)

            # save results to json
            pts_boundary_LOW = utils.get_mesh_vertex_coords_with_attribute(mesh, 'boundary', 1)
            pts_boundary_HIGH = utils.get_mesh_vertex_coords_with_attribute(mesh, 'boundary', 2)
            utils.save_to_json(utils.point_list_to_dict(pts_boundary_LOW), self.OUTPUT_PATH,
                               f'pts_boundary_LOW_{index}.json')
            utils.save_to_json(utils.point_list_to_dict(pts_boundary_HIGH), self.OUTPUT_PATH,
                               f'pts_boundary_HIGH_{index}.json')


# ---- utils

def get_union_method(params_dict: dict[str, Any]) -> tuple[str, list[Any]]:
    """
    Read input params_dict and return union method id and its parameters.
    target_type: LOW/HIGH
    """
    smooth_union_data = get_param(params_dict, key='target_HIGH_smooth_union', defaults_type='interpolation_slicing')
    chamfer_union_data = get_param(params_dict, key='target_HIGH_chamfer_union', defaults_type='interpolation_slicing')
    stairs_union_data = get_param(params_dict, key='target_HIGH_stairs_union', defaults_type='interpolation_slicing')
    if smooth_union_data[0]:
        method = 'smooth'
        params = smooth_union_data[1]
        assert not chamfer_union_data[0] and not stairs_union_data[0], 'You can only select one union method.'
        assert len(params) == 1, 'Wrong number of union params'
        return method, params
    elif chamfer_union_data[0]:
        method = 'chamfer'
        params = chamfer_union_data[1]
        assert not smooth_union_data[0] and not stairs_union_data[0], 'You can only select one union method.'
        assert len(params) == 1, 'Wrong number of union params'
        return method, params
    elif stairs_union_data[0]:
        method = 'stairs'
        params = stairs_union_data[1]
        assert not smooth_union_data[0] and not chamfer_union_data[0], 'You can only select one union method.'
        assert len(params) == 2, 'Wrong number of union params'
        return method, params
    else:
        method = 'min'
        params = []
        return method, params


if __name__ == "__main__":
    pass
