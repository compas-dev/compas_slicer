from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np

import compas_slicer.utilities.utils as utils
from compas_slicer.geometry.path import Path

if TYPE_CHECKING:
    from numpy.typing import NDArray

logger = logging.getLogger("logger")

__all__ = ["Layer", "VerticalLayer", "VerticalLayersManager"]


class Layer:
    """A Layer stores a group of ordered paths generated when a geometry is sliced.

    Layers are typically organized horizontally, but can also be organized
    vertically (see VerticalLayer). A Layer consists of one or multiple Paths.

    Attributes
    ----------
    paths : list[Path]
        List of paths in this layer.
    is_brim : bool
        True if this layer is a brim layer.
    number_of_brim_offsets : int | None
        The number of brim offsets this layer has (None if no brim).
    is_raft : bool
        True if this layer is a raft layer.
    min_max_z_height : tuple[float | None, float | None]
        Tuple containing the min and max z height of the layer.

    """

    def __init__(self, paths: list[Path] | None = None) -> None:
        if paths is None:
            paths = []
        if len(paths) > 0 and not isinstance(paths[0], Path):
            raise TypeError("paths must contain Path objects")

        self.paths = paths
        self.min_max_z_height: tuple[float | None, float | None] = (None, None)

        if paths:
            self.calculate_z_bounds()

        self.is_brim = False
        self.number_of_brim_offsets: int | None = None
        self.is_raft = False

    def __repr__(self) -> str:
        no_of_paths = len(self.paths) if self.paths else 0
        return f"<Layer object with {no_of_paths} paths>"

    @property
    def total_number_of_points(self) -> int:
        """Returns the total number of points within the layer."""
        return sum(len(path.points) for path in self.paths)

    def calculate_z_bounds(self) -> None:
        """Fills in the attribute self.min_max_z_height."""
        if not self.paths:
            raise ValueError("Cannot calculate z_bounds because the list of paths is empty.")

        z_min = float("inf")
        z_max = float("-inf")
        for path in self.paths:
            for pt in path.points:
                z_min = min(z_min, pt[2])
                z_max = max(z_max, pt[2])
        self.min_max_z_height = (z_min, z_max)

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> Layer:
        """Construct a layer from its data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        Layer
            The constructed layer.

        """
        paths_data = data["paths"]
        paths = [Path.from_data(paths_data[key]) for key in paths_data]
        layer = cls(paths=paths)
        layer.is_brim = data["is_brim"]
        layer.number_of_brim_offsets = data["number_of_brim_offsets"]
        layer.min_max_z_height = tuple(data["min_max_z_height"])
        return layer

    def to_data(self) -> dict[str, Any]:
        """Returns a dictionary of structured data representing the layer.

        Returns
        -------
        dict
            The layer's data.

        """
        return {
            "paths": {i: path.to_data() for i, path in enumerate(self.paths)},
            "layer_type": "horizontal_layer",
            "is_brim": self.is_brim,
            "number_of_brim_offsets": self.number_of_brim_offsets,
            "min_max_z_height": self.min_max_z_height,
        }


class VerticalLayer(Layer):
    """Vertical ordering layer that stores print paths sorted in vertical groups.

    It is created with an empty list of paths that is filled in afterwards.

    Attributes
    ----------
    id : int
        Identifier of vertical layer.
    head_centroid : NDArray | None
        Centroid of the last path's points.

    """

    def __init__(self, id: int = 0, paths: list[Path] | None = None) -> None:
        super().__init__(paths=paths)
        self.id = id
        self.head_centroid: NDArray | None = None

    def __repr__(self) -> str:
        no_of_paths = len(self.paths) if self.paths else 0
        return f"<Vertical Layer object with id: {self.id} and {no_of_paths} paths>"

    def append_(self, path: Path) -> None:
        """Add path to self.paths list."""
        self.paths.append(path)
        self.compute_head_centroid()
        self.calculate_z_bounds()

    def compute_head_centroid(self) -> None:
        """Find the centroid of all the points of the last path."""
        pts = np.array(self.paths[-1].points)
        self.head_centroid = np.mean(pts, axis=0)

    def printout_details(self) -> None:
        """Prints the details of the class."""
        logger.info(f"VerticalLayer id: {self.id}")
        logger.info(f"Total number of paths: {len(self.paths)}")

    def to_data(self) -> dict[str, Any]:
        """Returns a dictionary of structured data representing the vertical layer.

        Returns
        -------
        dict
            The vertical layer's data.

        """
        return {
            "paths": {i: path.to_data() for i, path in enumerate(self.paths)},
            "min_max_z_height": self.min_max_z_height,
            "layer_type": "vertical_layer",
        }

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> VerticalLayer:
        """Construct a vertical layer from its data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        VerticalLayer
            The constructed vertical layer.

        """
        paths_data = data["paths"]
        paths = [Path.from_data(paths_data[key]) for key in paths_data]
        layer = cls(id=0)
        layer.paths = paths
        layer.min_max_z_height = tuple(data["min_max_z_height"])
        return layer


class VerticalLayersManager:
    """Creates and manages vertical layers, assigning paths to fitting layers.

    The criterion for grouping paths to VerticalLayers is based on the
    proximity of the centroids of the paths. If the input paths don't fit
    in any vertical layer, then a new vertical layer is created.

    Attributes
    ----------
    layers : list[VerticalLayer]
        List of vertical layers.
    avg_layer_height : float
        Average layer height for proximity calculations.
    max_paths_per_layer : int | None
        Maximum number of paths per vertical layer. If None, unlimited.

    """

    def __init__(self, avg_layer_height: float, max_paths_per_layer: int | None = None) -> None:
        self.layers: list[VerticalLayer] = [VerticalLayer(id=0)]
        self.avg_layer_height = avg_layer_height
        self.max_paths_per_layer = max_paths_per_layer

    def add(self, path: Path) -> None:
        """Add a path to the appropriate vertical layer."""
        selected_layer: VerticalLayer | None = None

        # Find an eligible layer for path
        if len(self.layers[0].paths) == 0:
            selected_layer = self.layers[0]
        else:
            centroid = np.mean(np.array(path.points), axis=0)
            other_centroids = get_vertical_layers_centroids_list(self.layers)
            candidate_layer = self.layers[utils.get_closest_pt_index(centroid, other_centroids)]

            threshold_max_centroid_dist = 5 * self.avg_layer_height
            if np.linalg.norm(candidate_layer.head_centroid - centroid) < threshold_max_centroid_dist:
                if self.max_paths_per_layer:
                    if len(candidate_layer.paths) < self.max_paths_per_layer:
                        selected_layer = candidate_layer
                else:
                    selected_layer = candidate_layer

                if selected_layer:
                    # Check that actual distance between layers is acceptable
                    pts_selected_layer = np.array(candidate_layer.paths[-1].points)
                    pts = np.array(path.points)

                    min_dist = float("inf")
                    max_dist = 0.0
                    for pt in pts:
                        pt_array = np.tile(pt, (pts_selected_layer.shape[0], 1))
                        dists = np.linalg.norm(pts_selected_layer - pt_array, axis=1)
                        min_dist = min(np.min(dists), min_dist)
                        max_dist = max(np.min(dists), max_dist)

                    if min_dist > 3.0 * self.avg_layer_height or max_dist > 8.0 * self.avg_layer_height:
                        selected_layer = None

            if not selected_layer:
                selected_layer = VerticalLayer(id=self.layers[-1].id + 1)
                self.layers.append(selected_layer)

        selected_layer.append_(path)


def get_vertical_layers_centroids_list(vert_layers: list[VerticalLayer]) -> list[NDArray]:
    """Returns a list of centroids of the heads of all vertical layers.

    The head of a vertical_layer is its last path.

    Parameters
    ----------
    vert_layers : list[VerticalLayer]
        List of vertical layers.

    Returns
    -------
    list[NDArray]
        List of head centroids.

    """
    return [vert_layer.head_centroid for vert_layer in vert_layers]
