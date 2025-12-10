from __future__ import annotations

from loguru import logger
from pathlib import Path as FilePath
from typing import TYPE_CHECKING, Any

import numpy as np
from compas.geometry import (
    Point,
    Polyline,
    Vector,
    closest_point_on_polyline,
    distance_point_point,
    dot_vectors,
    scale_vector,
    subtract_vectors,
)
from numpy.typing import NDArray

# Check for CGAL availability at module load
_USE_CGAL = False
try:
    from compas_cgal.polylines import closest_points_on_polyline as _cgal_closest
    _USE_CGAL = True
except ImportError:
    _cgal_closest = None


def _batch_closest_points_on_polyline(
    query_points: list[Point], polyline_points: list[Point]
) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
    """Find closest points on polyline for batch of query points.

    Returns closest points and distances.
    Uses CGAL if available, otherwise falls back to compas.
    """
    if _USE_CGAL and len(query_points) > 10:
        # Use CGAL batch query for larger sets
        queries = [[p[0], p[1], p[2]] for p in query_points]
        polyline = [[p[0], p[1], p[2]] for p in polyline_points]
        closest = _cgal_closest(queries, polyline)
        # Compute distances
        queries_np = np.array(queries)
        distances = np.linalg.norm(closest[:, :2] - queries_np[:, :2], axis=1)
        return closest, distances
    else:
        # Fall back to per-point compas queries
        polyline = Polyline(polyline_points)
        closest = []
        distances = []
        for p in query_points:
            cp = closest_point_on_polyline(p, polyline)
            closest.append([cp[0], cp[1], cp[2]])
            distances.append(distance_point_point(cp, p))
        return np.array(closest), np.array(distances)

import compas_slicer.utilities as utils
from compas_slicer.geometry import Path, PrintLayer, PrintPath, PrintPoint, VerticalLayer
from compas_slicer.parameters import get_param
from compas_slicer.pre_processing.preprocessing_utils import topological_sorting as topo_sort
from compas_slicer.print_organization.base_print_organizer import BasePrintOrganizer
from compas_slicer.print_organization.curved_print_organization import BaseBoundary

if TYPE_CHECKING:
    from compas_slicer.slicers import InterpolationSlicer


__all__ = ['InterpolationPrintOrganizer']


class InterpolationPrintOrganizer(BasePrintOrganizer):
    """Organize the printing process for non-planar contours.

    Attributes
    ----------
    slicer : InterpolationSlicer
        An instance of InterpolationSlicer.
    parameters : dict[str, Any]
        Parameters dictionary.
    DATA_PATH : str | Path
        Data directory path.
    vertical_layers : list[VerticalLayer]
        Vertical layers from slicer.
    horizontal_layers : list[Layer]
        Horizontal layers from slicer.
    base_boundaries : list[BaseBoundary]
        Base boundaries for each vertical layer.

    """

    slicer: InterpolationSlicer

    def __init__(
        self,
        slicer: InterpolationSlicer,
        parameters: dict[str, Any],
        DATA_PATH: str | FilePath,
    ) -> None:
        from compas_slicer.slicers import InterpolationSlicer

        if not isinstance(slicer, InterpolationSlicer):
            raise TypeError('Please provide an InterpolationSlicer')
        BasePrintOrganizer.__init__(self, slicer)
        self.DATA_PATH = DATA_PATH
        self.OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
        self.parameters = parameters

        self.vertical_layers = slicer.vertical_layers
        self.horizontal_layers = slicer.horizontal_layers
        assert len(self.vertical_layers) + len(self.horizontal_layers) == len(slicer.layers)

        if len(self.horizontal_layers) > 0:
            assert len(self.horizontal_layers) == 1, "Only one brim horizontal layer is currently supported."
            assert self.horizontal_layers[0].is_brim, "Only one brim horizontal layer is currently supported."
            logger.info('Slicer has one horizontal brim layer.')

        # topological sorting of vertical layers depending on their connectivity
        self.topo_sort_graph: topo_sort.SegmentsDirectedGraph | None = None
        if len(self.vertical_layers) > 1:
            try:
                self.topological_sorting()
            except AssertionError:
                logger.exception("topology sorting failed\n")
                logger.critical("integrity of the output data ")
                # TODO: perhaps its better to be even more explicit and add a
                #  FAILED-timestamp.txt file?
        self.selected_order: list[int] | None = None

        # creation of one base boundary per vertical_layer
        self.base_boundaries: list[BaseBoundary] = self.create_base_boundaries()

    def __repr__(self) -> str:
        return f"<InterpolationPrintOrganizer with {len(self.vertical_layers)} vertical_layers>"

    def topological_sorting(self) -> None:
        """Create directed graph of parts with connectivity.

        Creates a directed graph where each part's connectivity reflects which
        other parts it lies on and which other parts lie on it.

        """
        avg_layer_height = get_param(self.parameters, key='avg_layer_height', defaults_type='layers')
        self.topo_sort_graph = topo_sort.SegmentsDirectedGraph(self.slicer.mesh, self.vertical_layers,
                                                               4 * avg_layer_height, DATA_PATH=self.DATA_PATH)

    def create_base_boundaries(self) -> list[BaseBoundary]:
        """Create one BaseBoundary per vertical_layer."""
        bs: list[BaseBoundary] = []
        root_vs = utils.get_mesh_vertex_coords_with_attribute(self.slicer.mesh, 'boundary', 1)
        root_boundary = BaseBoundary(self.slicer.mesh, [Point(*v) for v in root_vs])

        if len(self.vertical_layers) > 1 and self.topo_sort_graph is not None:
            for i, _vertical_layer in enumerate(self.vertical_layers):
                parents_of_current_node = self.topo_sort_graph.get_parents_of_node(i)
                if len(parents_of_current_node) == 0:
                    boundary = root_boundary
                else:
                    boundary_pts = []
                    for parent_index in parents_of_current_node:
                        parent = self.vertical_layers[parent_index]
                        boundary_pts.extend(parent.paths[-1].points)
                    boundary = BaseBoundary(self.slicer.mesh, boundary_pts)
                bs.append(boundary)
        else:
            bs.append(root_boundary)

        # save intermediary outputs
        b_data = {i: b.to_data() for i, b in enumerate(bs)}
        utils.save_to_json(b_data, self.OUTPUT_PATH, 'boundaries.json')

        return bs

    def create_printpoints(self) -> None:
        """Create the print points of the fabrication process.

        Based on the directed graph, select one topological order.
        From each path collection in that order, copy PrintPoints in the correct order.

        """
        current_layer_index = 0

        # (1) --- First add the printpoints of the horizontal brim layer (first layer of print)
        if len(self.horizontal_layers) > 0:  # first add horizontal brim layers
            print_layer = PrintLayer()
            paths = self.horizontal_layers[0].paths
            for _j, path in enumerate(paths):
                print_path = PrintPath(printpoints=[
                    PrintPoint(pt=point, layer_height=get_param(self.parameters, 'avg_layer_height', 'layers'),
                               mesh_normal=utils.get_normal_of_path_on_xy_plane(k, point, path, self.slicer.mesh))
                    for k, point in enumerate(path.points)
                ])
                print_layer.paths.append(print_path)
            self.printpoints.layers.append(print_layer)
            current_layer_index += 1
        else:
            # Add empty first layer placeholder if no horizontal layers
            pass

        # (2) --- Select order of vertical layers
        if len(self.vertical_layers) > 1:  # then you need to select one topological order

            if not self.topo_sort_graph:
                logger.error("no topology graph found, cannnot set the order of vertical layers")
                self.selected_order = [0]
            else:
                all_orders = self.topo_sort_graph.get_all_topological_orders()
                self.selected_order = all_orders[0]  # TODO: add more elaborate selection strategy
        else:
            self.selected_order = [0]  # there is only one segment, only this option

        # (3) --- Then create the printpoints of all the vertical layers in the selected order
        assert self.selected_order is not None, "selected_order must be set before creating printpoints"
        for _index, i in enumerate(self.selected_order):
            layer = self.vertical_layers[i]
            print_layer = self.get_layer_ppts(layer, self.base_boundaries[i])
            self.printpoints.layers.append(print_layer)
            current_layer_index += 1

    def get_layer_ppts(self, layer: VerticalLayer, base_boundary: BaseBoundary) -> PrintLayer:
        """Create the PrintPoints of a single layer."""
        max_layer_height = get_param(self.parameters, key='max_layer_height', defaults_type='layers')
        min_layer_height = get_param(self.parameters, key='min_layer_height', defaults_type='layers')
        avg_layer_height = get_param(self.parameters, 'avg_layer_height', 'layers')

        all_pts = [pt for path in layer.paths for pt in path.points]
        closest_fks, projected_pts = utils.pull_pts_to_mesh_faces(self.slicer.mesh, all_pts)
        normals = [Vector(*self.slicer.mesh.face_normal(fkey)) for fkey in closest_fks]

        count = 0
        support_polyline_pts = base_boundary.points  # Start with base boundary

        print_layer = PrintLayer()
        for _i, path in enumerate(layer.paths):
            # Batch query: find closest points for all points in this path at once
            closest_pts, distances = _batch_closest_points_on_polyline(
                path.points, support_polyline_pts
            )

            print_path = PrintPath()
            for k, p in enumerate(path.points):
                cp = closest_pts[k]
                d = distances[k]

                normal = normals[count]
                ppt = PrintPoint(pt=p, layer_height=avg_layer_height, mesh_normal=normal)

                ppt.closest_support_pt = Point(cp[0], cp[1], cp[2])
                ppt.distance_to_support = d
                ppt.layer_height = max(min(d, max_layer_height), min_layer_height)
                ppt.up_vector = self.get_printpoint_up_vector(path, k, normal)
                if dot_vectors(subtract_vectors(p, ppt.closest_support_pt), ppt.up_vector) < 0:
                    ppt.up_vector = Vector(*scale_vector(ppt.up_vector, -1))
                ppt.frame = ppt.get_frame()

                print_path.printpoints.append(ppt)
                count += 1

            print_layer.paths.append(print_path)
            support_polyline_pts = path.points  # Next path checks against this one

        return print_layer


if __name__ == "__main__":
    pass
