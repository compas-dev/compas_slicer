from __future__ import annotations

from abc import abstractmethod
from pathlib import Path as FilePath
from typing import TYPE_CHECKING, Any

from compas.geometry import Point, distance_point_point_sqrd
from compas.itertools import pairwise

import compas_slicer.utilities as utils
from compas_slicer.geometry import Path, VerticalLayersManager
from compas_slicer.slicers.slice_utilities.graph_connectivity import (
    create_graph_from_mesh_edges,
    sort_graph_connected_components,
)

if TYPE_CHECKING:
    from compas.datastructures import Mesh


__all__ = ["ContoursBase"]


class ContoursBase:
    """
    This is meant to be extended by all classes that generate isocontours of a scalar function on a mesh.
    This class handles the two steps of iso-contouring of a triangular mesh consists of two steps;
    1)find intersected edges and 2)sort intersections using a graph to generate coherent polylines.

    The inheriting classes only have to implement the test that checks if an edge is intersected,
    and the method to find the zero crossing of an intersection.

    Attributes
    ----------
    mesh : :class: 'compas.datastructures.Mesh'

    """

    def __init__(self, mesh: Mesh) -> None:
        self.mesh = mesh
        self.intersection_data: dict[tuple[int, int], Point] = {}
        # key: tuple (int, int), The edge from which the intersection point originates.
        # value: :class: 'compas.geometry.Point', The zero-crossing point.
        self.edge_to_index: dict[tuple[int, int], int] = {}
        # key: tuple (int, int) edge
        # value: int, index of the intersection point
        self.sorted_point_clusters: dict[int, list[Point]] = {}
        # key: int, The index of the connected component
        # value: list, :class: 'compas.geometry.Point', The sorted zero-crossing points.
        self.sorted_edge_clusters: dict[int, list[tuple[int, int]]] = {}
        # key: int, The index of the connected component.
        # value: list, tuple (int, int), The sorted intersected edges.
        self.closed_paths_booleans: dict[int, bool] = {}
        # key: int, The index of the connected component.
        # value: bool, True if path is closed, False otherwise.

    def compute(self) -> None:
        self.find_intersections()
        G = create_graph_from_mesh_edges(self.mesh, self.intersection_data, self.edge_to_index)
        sorted_indices_dict = sort_graph_connected_components(G)

        nodeDict = dict(G.nodes(data=True))
        for key in sorted_indices_dict:
            sorted_indices = sorted_indices_dict[key]
            self.sorted_edge_clusters[key] = [nodeDict[node_index]["mesh_edge"] for node_index in sorted_indices]
            self.sorted_point_clusters[key] = [self.intersection_data[e] for e in self.sorted_edge_clusters[key]]

        self.label_closed_paths()

    def label_closed_paths(self) -> None:
        for key in self.sorted_edge_clusters:
            first_edge = self.sorted_edge_clusters[key][0]
            last_edge = self.sorted_edge_clusters[key][-1]
            u, v = first_edge
            self.closed_paths_booleans[key] = u in last_edge or v in last_edge

    def find_intersections(self) -> None:
        """
        Fills in the
        dict self.intersection_data: key=(ui,vi) : [xi,yi,zi],
        dict self.edge_to_index: key=(u1,v1) : point_index."""
        for edge in list(self.mesh.edges()):
            if self.edge_is_intersected(edge[0], edge[1]):
                point = self.find_zero_crossing_data(edge[0], edge[1])
                if point and edge not in self.intersection_data and tuple(reversed(edge)) not in self.intersection_data:
                    # create [edge - point] dictionary
                    self.intersection_data[edge] = {}
                    self.intersection_data[edge] = Point(point[0], point[1], point[2])

            # create [edge - point] dictionary
            for i, e in enumerate(self.intersection_data):
                self.edge_to_index[e] = i

    def save_point_clusters_as_polylines_to_json(self, DATA_PATH: str | FilePath, name: str) -> None:
        all_points: dict[str, Any] = {}
        for i, key in enumerate(self.sorted_point_clusters):
            all_points[str(i)] = utils.point_list_to_dict(self.sorted_point_clusters[key])
        utils.save_to_json(all_points, DATA_PATH, name)

    # --- Abstract methods
    @abstractmethod
    def edge_is_intersected(self, u: int, v: int) -> bool:
        """Returns True if the edge u,v has a zero-crossing, False otherwise."""
        # to be implemented by the inheriting classes
        pass

    @abstractmethod
    def find_zero_crossing_data(self, u: int, v: int) -> list[float] | None:
        """Finds the position of the zero-crossing on the edge u,v."""
        # to be implemented by the inheriting classes
        pass

    def add_to_vertical_layers_manager(self, vertical_layers_manager: VerticalLayersManager) -> None:
        for key in self.sorted_point_clusters:
            pts = self.sorted_point_clusters[key]
            if len(pts) > 3:  # discard curves that are too small
                path = Path(pts, is_closed=self.closed_paths_booleans[key])

                vertical_layers_manager.add(path)

    @property
    def is_valid(self):
        if len(self.sorted_point_clusters) > 0:
            for key in self.sorted_point_clusters:
                pts = self.sorted_point_clusters[key]
                if len(pts) > 3:
                    path_total_length = 0.0
                    for p1, p2 in pairwise(pts):
                        path_total_length += distance_point_point_sqrd(p1, p2)
                    if path_total_length > 1.0:
                        return True  # make sure there is at least one path with acceptable length
        return False
