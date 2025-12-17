from __future__ import annotations

import math
import statistics
from typing import Any, Literal

import networkx as nx
import numpy as np
from compas.datastructures import Mesh
from loguru import logger
from numpy.typing import NDArray

import compas_slicer.utilities as utils
from compas_slicer.pre_processing.preprocessing_utils.geodesics import (
    get_cgal_HEAT_geodesic_distances,
    get_custom_HEAT_geodesic_distances,
    get_igl_EXACT_geodesic_distances,
    get_igl_HEAT_geodesic_distances,
)

GeodesicsMethod = Literal["exact_igl", "heat_igl", "heat_cgal", "heat"]
UnionMethod = Literal["min", "smooth", "chamfer", "stairs"]


def _create_graph_from_mesh_vkeys(mesh: Mesh, v_keys: list[int]) -> nx.Graph:
    """Creates a graph with one node for every vertex, and edges between neighboring vertices."""
    G = nx.Graph()
    [G.add_node(v) for v in v_keys]
    for v in v_keys:
        v_neighbors = mesh.vertex_neighbors(v)
        for other_v in v_neighbors:
            if other_v != v and other_v in v_keys:
                G.add_edge(v, other_v)
    return G


__all__ = ["CompoundTarget", "blend_union_list", "stairs_union_list", "chamfer_union_list"]


class CompoundTarget:
    """
    Represents a desired user-provided target. It acts as a key-frame that controls the print paths
    orientations. After the curved slicing , the print paths will be aligned to the compound target close to
    its area. The vertices that belong to the target are marked with their vertex attributes; they have
    data['v_attr'] = value.

    Attributes
    ----------
    mesh: :class:`compas.datastructures.Mesh`
    v_attr : str
        The key of the attribute dict to be checked.
    value: int
        The value of the attribute dict with key=v_attr. If in a vertex data[v_attr]==value then the vertex is part of
        this target.
    DATA_PATH: str
    has_blend_union: bool
    blend_radius : float
    geodesics_method: str
        'heat_cgal'  CGAL heat geodesic distances (recommended)
        'heat'       custom heat geodesic distances
    anisotropic_scaling: bool
        This is not yet implemented
    """

    def __init__(
        self,
        mesh: Mesh,
        v_attr: str,
        value: int,
        DATA_PATH: str,
        union_method: UnionMethod = "min",
        union_params: list[Any] | None = None,
        geodesics_method: GeodesicsMethod = "heat_cgal",
        anisotropic_scaling: bool = False,
    ) -> None:
        if union_params is None:
            union_params = []
        logger.info(f"Creating target with attribute : {v_attr}={value}")
        logger.info(f"union_method: {union_method}, union_params: {union_params}")
        self.mesh = mesh
        self.v_attr = v_attr
        self.value = value
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)

        self.union_method = union_method
        self.union_params = union_params

        self.geodesics_method = geodesics_method
        self.anisotropic_scaling = anisotropic_scaling  # Anisotropic scaling not yet implemented

        self.offset = 0
        self.VN = len(list(self.mesh.vertices()))

        # filled in by function 'self.find_targets_connected_components()'
        self.all_target_vkeys: list[int] = []  # flattened list with all vi_starts
        self.clustered_vkeys: list[list[int]] = []  # nested list with all vi_starts
        self.number_of_boundaries: int = 0

        self.weight_max_per_cluster: list[float] = []

        # geodesic distances
        # filled in by function 'self.update_distances_lists()'
        self._distances_lists: list[list[float]] = []  # Shape: number_of_boundaries x number_of_vertices
        self._distances_lists_flipped: list[list[float]] = []  # Shape: number_of_vertices x number_of_boundaries
        self._np_distances_lists_flipped: NDArray[np.floating] = np.array([])
        self._max_dist: float | None = None  # maximum distance from target on any mesh vertex

        # compute
        self.find_targets_connected_components()
        self.compute_geodesic_distances()

    #  --- Neighborhoods clustering
    def find_targets_connected_components(self) -> None:
        """
        Clusters all the vertices that belong to the target into neighborhoods using a graph.
        Each target can have an arbitrary number of neighborhoods/clusters.
        Fills in the attributes: self.all_target_vkeys, self.clustered_vkeys, self.number_of_boundaries
        """
        self.all_target_vkeys = [
            vkey for vkey, data in self.mesh.vertices(data=True) if data[self.v_attr] == self.value
        ]
        if len(self.all_target_vkeys) == 0:
            raise ValueError(
                f"No vertices in mesh with attribute '{self.v_attr}'={self.value}. Check your target creation."
            )
        G = _create_graph_from_mesh_vkeys(self.mesh, self.all_target_vkeys)
        if len(list(G.nodes())) != len(self.all_target_vkeys):
            raise RuntimeError("Graph node count doesn't match target vertex count.")
        self.number_of_boundaries = len(list(nx.connected_components(G)))

        for _i, cp in enumerate(nx.connected_components(G)):
            self.clustered_vkeys.append(list(cp))
        logger.info(
            f"Compound target with 'boundary'={self.value}. Number of connected_components : "
            f"{len(list(nx.connected_components(G)))}"
        )

    #  --- Geodesic distances
    def compute_geodesic_distances(self) -> None:
        """
        Computes the geodesic distances from each of the target's neighborhoods  to all the mesh vertices.
        Fills in the distances attributes.
        """
        if self.geodesics_method == "exact_igl":
            distances_lists = [get_igl_EXACT_geodesic_distances(self.mesh, vstarts) for vstarts in self.clustered_vkeys]
        elif self.geodesics_method == "heat_igl":
            distances_lists = [get_igl_HEAT_geodesic_distances(self.mesh, vstarts) for vstarts in self.clustered_vkeys]
        elif self.geodesics_method == "heat_cgal":
            distances_lists = [get_cgal_HEAT_geodesic_distances(self.mesh, vstarts) for vstarts in self.clustered_vkeys]
        elif self.geodesics_method == "heat":
            distances_lists = [
                get_custom_HEAT_geodesic_distances(self.mesh, vstarts, str(self.OUTPUT_PATH))
                for vstarts in self.clustered_vkeys
            ]
        else:
            raise ValueError("Unknown geodesics method : " + self.geodesics_method)

        distances_lists = [list(dl) for dl in distances_lists]  # number_of_boundaries x #V
        self.update_distances_lists(distances_lists)

    def update_distances_lists(self, distances_lists: list[list[float]]) -> None:
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
    def has_uneven_weights(self) -> bool:
        """Returns True if the target has uneven_weights calculated, False otherwise."""
        return len(self.weight_max_per_cluster) > 0

    def compute_uneven_boundaries_weight_max(self, other_target: CompoundTarget) -> None:
        """
        If the target has multiple neighborhoods/clusters of vertices, then it computes their maximum distance from
        the other_target. Based on that it calculates their weight_max for the interpolation process
        """
        if self.number_of_boundaries > 1:
            ds_avg_HIGH = self.get_boundaries_rel_dist_from_other_target(other_target)
            max_param = max(ds_avg_HIGH)
            for i, d in enumerate(ds_avg_HIGH):  # offset all distances except the maximum one
                if abs(d - max_param) > 0.01:  # if it isn't the max value
                    ds_avg_HIGH[i] = d + self.offset

            self.weight_max_per_cluster = [d / max_param for d in ds_avg_HIGH]
            logger.info(f"weight_max_per_cluster: {self.weight_max_per_cluster}")
        else:
            logger.info("Did not compute_norm_of_gradient uneven boundaries, target consists of single component")

    #  --- Relation to other target
    def get_boundaries_rel_dist_from_other_target(
        self, other_target: CompoundTarget, avg_type: Literal["mean", "median"] = "median"
    ) -> list[float]:
        """
        Returns a list, one relative distance value per connected boundary neighborhood.
        That is the average of the distances of the vertices of that boundary neighborhood from the other_target.
        """
        distances = []
        for vi_starts in self.clustered_vkeys:
            ds = [other_target.get_distance(vi) for vi in vi_starts]
            if avg_type == "mean":
                distances.append(statistics.mean(ds))
            else:  # 'median'
                distances.append(statistics.median(ds))
        return distances

    def get_avg_distances_from_other_target(self, other_target: CompoundTarget) -> float:
        """
        Returns the minimum and maximum distance of the vertices of this target from the other_target
        """
        extreme_distances = []
        for v_index in other_target.all_target_vkeys:
            extreme_distances.append(self.get_all_distances()[v_index])
        return float(np.average(np.array(extreme_distances)))

    #############################
    #  --- get all distances

    def get_all_clusters_distances_dict(self) -> dict[int, list[float]]:
        """Returns dict. keys: index of connected target neighborhood, value: list, distances (one per vertex)."""
        return {i: self._distances_lists[i] for i in range(self.number_of_boundaries)}

    def get_max_dist(self) -> float | None:
        """Returns the maximum distance that the target has on a mesh vertex."""
        return self._max_dist

    #############################
    #  --- vectorized distances (all vertices at once)

    def get_all_distances(self) -> np.ndarray:
        """Return distances for all vertices as 1D array, applying union method."""
        if self.union_method == "min":
            return np.min(self._np_distances_lists_flipped, axis=1)
        elif self.union_method == "smooth":
            return np.array(
                [blend_union_list(row.tolist(), self.union_params[0]) for row in self._np_distances_lists_flipped]
            )
        elif self.union_method == "chamfer":
            return np.array(
                [chamfer_union_list(row.tolist(), self.union_params[0]) for row in self._np_distances_lists_flipped]
            )
        elif self.union_method == "stairs":
            return np.array(
                [
                    stairs_union_list(row.tolist(), self.union_params[0], self.union_params[1])
                    for row in self._np_distances_lists_flipped
                ]
            )
        else:
            raise ValueError(f"Unknown union method: {self.union_method}")

    def get_all_distances_array(self) -> np.ndarray:
        """Return raw distances as (n_boundaries, n_vertices) array."""
        return np.array(self._distances_lists)

    #############################
    #  --- per vkey distances

    def get_all_distances_for_vkey(self, i: int) -> list[float]:
        """Returns distances from each cluster separately for vertex i. Smooth union doesn't play here any role."""
        return [self._distances_lists[list_index][i] for list_index in range(self.number_of_boundaries)]

    def get_distance(self, i: int) -> float:
        """Return get_distance for vertex with vkey i."""
        if self.union_method == "min":
            # --- simple union
            return float(np.min(self._np_distances_lists_flipped[i]))
        elif self.union_method == "smooth":
            # --- blend (smooth) union
            return blend_union_list(values=self._np_distances_lists_flipped[i], r=self.union_params[0])
        elif self.union_method == "chamfer":
            # --- blend (smooth) union
            return chamfer_union_list(values=self._np_distances_lists_flipped[i], r=self.union_params[0])
        elif self.union_method == "stairs":
            # --- stairs union
            return stairs_union_list(
                values=self._np_distances_lists_flipped[i], r=self.union_params[0], n=self.union_params[1]
            )
        else:
            raise ValueError("Unknown Union method : ", self.union_method)

    #############################
    #  --- scalar field smoothing

    def laplacian_smoothing(self, iterations: int, strength: float) -> None:
        """Smooth the distances on the mesh, using iterative laplacian smoothing."""
        L = utils.get_mesh_cotmatrix_igl(self.mesh, fix_boundaries=True)
        new_distances_lists = []

        logger.info("Laplacian smoothing of all distances")
        for _i, a in enumerate(self._distances_lists):
            a = np.array(a)  # a: numpy array containing the attribute to be smoothed
            for _ in range(iterations):  # iterative smoothing
                a_prime = a + strength * L * a
                a = a_prime
            new_distances_lists.append(list(a))
        self.update_distances_lists(new_distances_lists)

    #############################
    #  ------ output
    def save_distances(self, name: str) -> None:
        """
        Save distances to json.
        Saves one list with distance values (one per vertex).

        Parameters
        ----------
        name: str, name of json to be saved
        """
        utils.save_to_json(self.get_all_distances().tolist(), self.OUTPUT_PATH, name)

    #  ------ assign new Mesh
    def assign_new_mesh(self, mesh: Mesh) -> None:
        """When the base mesh changes, a new mesh needs to be assigned."""
        mesh.to_json(self.OUTPUT_PATH + "/temp.obj")
        mesh = Mesh.from_json(self.OUTPUT_PATH + "/temp.obj")
        self.mesh = mesh
        self.VN = len(list(self.mesh.vertices()))


####################
#  unions on lists


def blend_union_list(values: NDArray[np.floating] | list[float], r: float) -> float:
    """Returns a smooth union of all the elements in the list, with blend radius blend_radius."""
    d_result: float = 9999999.0  # very big number
    for d in values:
        d_result = blend_union(d_result, float(d), r)
    return d_result


def stairs_union_list(values: NDArray[np.floating] | list[float], r: float, n: int) -> float:
    """Returns a stairs union of all the elements in the list, with blend radius r and number of peaks n-1."""
    d_result: float = 9999999.0  # very big number
    for _i, d in enumerate(values):
        d_result = stairs_union(d_result, float(d), r, n)
    return d_result


def chamfer_union_list(values: NDArray[np.floating] | list[float], r: float) -> float:
    d_result: float = 9999999.0  # very big number
    for _i, d in enumerate(values):
        d_result = chamfer_union(d_result, float(d), r)
    return d_result


####################
#  unions on pairs


def blend_union(da: float, db: float, r: float) -> float:
    """Returns a smooth union of the two elements da, db with blend radius blend_radius."""
    e = max(r - abs(da - db), 0)
    return min(da, db) - e * e * 0.25 / r


def chamfer_union(a: float, b: float, r: float) -> float:
    """Returns a chamfer union of the two elements da, db with radius r."""
    return min(min(a, b), (a - r + b) * math.sqrt(0.5))


def stairs_union(a: float, b: float, r: float, n: int) -> float:
    """Returns a stairs union of the two elements da, db with radius r."""
    s = r / n
    u = b - r
    return min(min(a, b), 0.5 * (u + a + abs((u - a + s) % (2 * s) - s)))


if __name__ == "__main__":
    pass
