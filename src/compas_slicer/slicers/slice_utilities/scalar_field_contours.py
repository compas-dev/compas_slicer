from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from compas.geometry import Point, Polyline

from compas_slicer.geometry import Path, VerticalLayersManager

if TYPE_CHECKING:
    from compas.datastructures import Mesh

__all__ = ["ScalarFieldContours"]


class ScalarFieldContours:
    """Finds iso-contours of vertex scalar field using CGAL backend.

    Extracts zero-level isolines from the 'scalar_field' vertex attribute.

    Parameters
    ----------
    mesh : Mesh
        Triangular mesh with 'scalar_field' vertex attribute.

    """

    def __init__(self, mesh: Mesh) -> None:
        self.mesh = mesh
        self.polylines: list[Polyline] = []
        self._closed_flags: list[bool] = []

    def compute(self) -> None:
        """Extract zero-level isolines from scalar field."""
        from compas_cgal.isolines import isolines

        results = isolines(self.mesh, "scalar_field", isovalues=[0.0])

        for pts in results:
            points = [Point(*p) for p in pts.tolist()]
            self.polylines.append(Polyline(points))
            is_closed = bool(np.linalg.norm(pts[0] - pts[-1]) < 1e-6)
            self._closed_flags.append(is_closed)

    def add_to_vertical_layers_manager(self, manager: VerticalLayersManager) -> None:
        """Add isolines to a VerticalLayersManager.

        Parameters
        ----------
        manager : VerticalLayersManager
            The manager to add paths to.

        """
        for polyline, is_closed in zip(self.polylines, self._closed_flags):
            if len(polyline.points) > 3:
                path = Path(polyline.points, is_closed=is_closed)
                manager.add(path)

    @property
    def is_valid(self) -> bool:
        """Check if any valid paths were found."""
        return any(len(pl.points) > 3 for pl in self.polylines)
