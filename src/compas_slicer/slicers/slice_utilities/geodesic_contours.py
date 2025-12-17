from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from compas.geometry import Point, Polyline

from compas_slicer.geometry import Path, VerticalLayersManager

if TYPE_CHECKING:
    from compas.datastructures import Mesh


__all__ = ["GeodesicContours"]


class GeodesicContours:
    """Extract geodesic isolines using compas_cgal.

    Parameters
    ----------
    mesh : Mesh
        Triangular mesh.
    sources : list[int]
        Source vertex indices.
    isovalues : list[float]
        Isovalue thresholds for isoline extraction.

    """

    def __init__(self, mesh: Mesh, sources: list[int], isovalues: list[float]) -> None:
        self.mesh = mesh
        self.sources = sources
        self.isovalues = isovalues
        self.polylines: list[Polyline] = []
        self._closed_flags: list[bool] = []

    def compute(self) -> None:
        """Compute geodesic isolines from sources at specified isovalues."""
        from compas_cgal.geodesics import geodesic_isolines

        V, F = self.mesh.to_vertices_and_faces()
        results = geodesic_isolines((V, F), self.sources, self.isovalues)

        for pts in results:
            points = [Point(*p) for p in pts.tolist()]
            self.polylines.append(Polyline(points))
            is_closed = bool(np.linalg.norm(pts[0] - pts[-1]) < 1e-6)
            self._closed_flags.append(is_closed)

    def add_to_vertical_layers_manager(self, manager: VerticalLayersManager) -> None:
        """Add computed isolines to a VerticalLayersManager.

        Parameters
        ----------
        manager : VerticalLayersManager
            The manager to add paths to.

        """
        for polyline, is_closed in zip(self.polylines, self._closed_flags):
            if len(polyline.points) > 3:
                path = Path(polyline.points, is_closed=is_closed)
                manager.add(path)
