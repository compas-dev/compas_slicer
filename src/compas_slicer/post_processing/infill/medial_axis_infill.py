"""Medial axis based infill generation using CGAL straight skeleton."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.geometry import Point, distance_point_point
from loguru import logger

from compas_slicer.geometry import Path

if TYPE_CHECKING:
    from compas.datastructures import Graph

    from compas_slicer.slicers import BaseSlicer


__all__ = ["generate_medial_axis_infill"]


def generate_medial_axis_infill(
    slicer: BaseSlicer,
    min_length: float = 5.0,
    include_bisectors: bool = True,
) -> None:
    """Generate medial axis infill paths for all layers.

    Uses CGAL's straight skeleton to compute the medial axis of each
    closed contour, then converts skeleton edges to infill paths.

    Parameters
    ----------
    slicer : BaseSlicer
        Slicer with layers containing boundary paths.
    min_length : float
        Minimum skeleton edge length to include. Shorter edges are skipped.
    include_bisectors : bool
        If True, include bisector edges (skeleton to boundary connections).
        If False, only include inner_bisector edges (skeleton internal edges).

    """
    from compas_cgal.straight_skeleton_2 import interior_straight_skeleton

    logger.info("Generating medial axis infill")

    for layer in slicer.layers:
        infill_paths: list[Path] = []

        for path in layer.paths:
            if not path.is_closed:
                continue

            # Convert path to 2D polygon
            polygon_2d = _path_to_polygon_2d(path)
            if len(polygon_2d) < 3:
                continue

            z_height = path.points[0][2]

            # Compute straight skeleton
            try:
                graph = interior_straight_skeleton(polygon_2d)
            except Exception as e:
                logger.warning(f"Skeleton failed for path: {e}")
                continue

            # Extract skeleton edges as paths
            skeleton_paths = _skeleton_to_paths(graph, z_height, min_length, include_bisectors)
            infill_paths.extend(skeleton_paths)

        # Add infill paths to layer
        layer.paths.extend(infill_paths)
        logger.info(f"Added {len(infill_paths)} infill paths to layer")


def _path_to_polygon_2d(path: Path) -> list[list[float]]:
    """Convert 3D Path to 2D polygon vertices.

    Parameters
    ----------
    path : Path
        Path with 3D points.

    Returns
    -------
    list[list[float]]
        2D polygon vertices (x, y, 0).

    """
    return [[pt[0], pt[1], 0.0] for pt in path.points]


def _skeleton_to_paths(
    graph: Graph,
    z_height: float,
    min_length: float,
    include_bisectors: bool,
) -> list[Path]:
    """Convert skeleton graph edges to Path objects.

    Parameters
    ----------
    graph : Graph
        Skeleton graph from CGAL.
    z_height : float
        Z height to assign to path points.
    min_length : float
        Minimum edge length to include.
    include_bisectors : bool
        If True, include bisector edges. If False, only inner_bisector edges.

    Returns
    -------
    list[Path]
        List of infill paths.

    """
    paths = []

    for edge in graph.edges():
        edge_attrs = graph.edge_attributes(edge)

        # Skip boundary edges (polygon edges)
        if edge_attrs.get("boundary"):
            continue

        # Check if this is a skeleton edge we want
        is_inner = edge_attrs.get("inner_bisector", False)
        is_bisector = edge_attrs.get("bisector", False)

        if not is_inner and not (include_bisectors and is_bisector):
            continue

        u, v = edge
        node_u = graph.node_attributes(u)
        node_v = graph.node_attributes(v)

        pt_u = Point(float(node_u["x"]), float(node_u["y"]), z_height)
        pt_v = Point(float(node_v["x"]), float(node_v["y"]), z_height)

        # Skip short edges
        if distance_point_point(pt_u, pt_v) < min_length:
            continue

        paths.append(Path(points=[pt_u, pt_v], is_closed=False))

    return paths
