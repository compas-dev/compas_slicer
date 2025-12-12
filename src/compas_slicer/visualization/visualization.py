"""Visualization utilities for compas_slicer using compas_viewer."""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import networkx as nx

if TYPE_CHECKING:
    from compas.datastructures import Mesh

    from compas_slicer.slicers import BaseSlicer

__all__ = ["should_visualize", "visualize_slicer", "plot_networkx_graph"]


def should_visualize() -> bool:
    """Check if visualization should run.

    Returns False when running under pytest.

    Returns
    -------
    bool
        True if visualization should be shown.

    """
    return "pytest" not in sys.modules


def visualize_slicer(
    slicer: BaseSlicer,
    mesh: Mesh | None = None,
    show_mesh: bool = True,
    mesh_opacity: float = 0.3,
) -> None:
    """Visualize slicer toolpaths in compas_viewer.

    Parameters
    ----------
    slicer : BaseSlicer
        Slicer with layers containing paths.
    mesh : Mesh, optional
        Mesh to display alongside paths.
    show_mesh : bool
        If True, display the mesh.
    mesh_opacity : float
        Opacity for mesh display (0-1).

    """
    from compas.colors import Color
    from compas.geometry import Polyline
    from compas_viewer import Viewer

    viewer = Viewer()

    # Add mesh if provided
    if mesh and show_mesh:
        viewer.scene.add(mesh, opacity=mesh_opacity)

    # Add paths as polylines with color gradient by layer
    n_layers = len(slicer.layers)
    for i, layer in enumerate(slicer.layers):
        t = i / max(n_layers - 1, 1)
        color = Color(t, 0.5, 1 - t)  # Blue -> Purple gradient

        for path in layer.paths:
            if len(path.points) > 1:
                pts = list(path.points)
                if path.is_closed and pts[0] != pts[-1]:
                    pts.append(pts[0])
                polyline = Polyline(pts)
                viewer.scene.add(polyline, linecolor=color, linewidth=1)

    viewer.show()


def plot_networkx_graph(G: nx.Graph) -> None:
    """Plot a networkx graph.

    Parameters
    ----------
    G : nx.Graph
        The graph to plot.

    """
    import matplotlib.pyplot as plt

    plt.subplot(121)
    nx.draw(G, with_labels=True, font_weight='bold', node_color=range(len(list(G.nodes()))))
    plt.show()
