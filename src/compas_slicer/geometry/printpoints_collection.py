from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from compas.data import Data

if TYPE_CHECKING:
    from compas_slicer.geometry import PrintPoint

__all__ = ["PrintPath", "PrintLayer", "PrintPointsCollection"]


@dataclass
class PrintPath(Data):
    """A collection of PrintPoints forming a continuous print path.

    Attributes
    ----------
    printpoints : list[PrintPoint]
        List of print points in this path.

    """

    printpoints: list[PrintPoint] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__init__()  # Initialize Data base class

    def __len__(self) -> int:
        return len(self.printpoints)

    def __iter__(self) -> Iterator[PrintPoint]:
        return iter(self.printpoints)

    def __getitem__(self, index: int) -> PrintPoint:
        return self.printpoints[index]

    def __repr__(self) -> str:
        return f"<PrintPath with {len(self.printpoints)} points>"

    @property
    def __data__(self) -> dict[str, Any]:
        return {
            "printpoints": [pp.__data__ for pp in self.printpoints],
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> PrintPath:
        from compas_slicer.geometry import PrintPoint

        return cls(
            printpoints=[PrintPoint.__from_data__(pp) for pp in data["printpoints"]],
        )


@dataclass
class PrintLayer(Data):
    """A layer containing multiple print paths.

    Attributes
    ----------
    paths : list[PrintPath]
        List of print paths in this layer.

    """

    paths: list[PrintPath] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__init__()  # Initialize Data base class

    def __len__(self) -> int:
        return len(self.paths)

    def __iter__(self) -> Iterator[PrintPath]:
        return iter(self.paths)

    def __getitem__(self, index: int) -> PrintPath:
        return self.paths[index]

    def __repr__(self) -> str:
        total_points = sum(len(path) for path in self.paths)
        return f"<PrintLayer with {len(self.paths)} paths, {total_points} points>"

    @property
    def __data__(self) -> dict[str, Any]:
        return {
            "paths": [path.__data__ for path in self.paths],
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> PrintLayer:
        return cls(
            paths=[PrintPath.__from_data__(p) for p in data["paths"]],
        )


@dataclass
class PrintPointsCollection(Data):
    """A collection of print layers, paths, and points.

    Replaces the old PrintPointsDict structure (dict[str, dict[str, list[PrintPoint]]]).

    Attributes
    ----------
    layers : list[PrintLayer]
        List of print layers.

    Example
    -------
    >>> collection[0].paths[1].printpoints[2]  # Access by index
    >>> for layer in collection:
    ...     for path in layer:
    ...         for pp in path:
    ...             print(pp.pt)

    """

    layers: list[PrintLayer] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__init__()  # Initialize Data base class

    def __len__(self) -> int:
        return len(self.layers)

    def __iter__(self) -> Iterator[PrintLayer]:
        return iter(self.layers)

    def __getitem__(self, index: int) -> PrintLayer:
        return self.layers[index]

    def __repr__(self) -> str:
        total_paths = sum(len(layer) for layer in self.layers)
        total_points = sum(len(path) for layer in self.layers for path in layer)
        return f"<PrintPointsCollection with {len(self.layers)} layers, {total_paths} paths, {total_points} points>"

    @property
    def number_of_layers(self) -> int:
        """Number of layers."""
        return len(self.layers)

    @property
    def number_of_paths(self) -> int:
        """Total number of paths across all layers."""
        return sum(len(layer) for layer in self.layers)

    @property
    def number_of_printpoints(self) -> int:
        """Total number of print points."""
        return sum(len(path) for layer in self.layers for path in layer)

    def iter_printpoints(self) -> Iterator[PrintPoint]:
        """Iterate over all printpoints in the collection.

        Yields
        ------
        PrintPoint
            Each printpoint in the collection.

        """
        for layer in self.layers:
            for path in layer:
                yield from path

    def iter_with_indices(self) -> Iterator[tuple[PrintPoint, int, int, int]]:
        """Iterate over printpoints with their indices.

        Yields
        ------
        tuple[PrintPoint, int, int, int]
            Tuple of (printpoint, layer_index, path_index, point_index).

        """
        for i, layer in enumerate(self.layers):
            for j, path in enumerate(layer):
                for k, pp in enumerate(path):
                    yield pp, i, j, k

    def get_printpoint(self, layer_idx: int, path_idx: int, pp_idx: int) -> PrintPoint:
        """Get a specific printpoint by indices.

        Parameters
        ----------
        layer_idx : int
            Layer index.
        path_idx : int
            Path index within the layer.
        pp_idx : int
            Printpoint index within the path.

        Returns
        -------
        PrintPoint
            The requested printpoint.

        """
        return self.layers[layer_idx].paths[path_idx].printpoints[pp_idx]

    def number_of_paths_on_layer(self, layer_idx: int) -> int:
        """Get the number of paths in a specific layer.

        Parameters
        ----------
        layer_idx : int
            Layer index.

        Returns
        -------
        int
            Number of paths in the layer.

        """
        return len(self.layers[layer_idx])

    @property
    def __data__(self) -> dict[str, Any]:
        return {
            "layers": [layer.__data__ for layer in self.layers],
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> PrintPointsCollection:
        return cls(
            layers=[PrintLayer.__from_data__(layer) for layer in data["layers"]],
        )

    def to_data(self) -> dict[str, Any]:
        """Returns a dictionary of structured data.

        Returns
        -------
        dict
            The collection's data.

        """
        return self.__data__

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> PrintPointsCollection:
        """Construct from data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        PrintPointsCollection
            The constructed collection.

        """
        return cls.__from_data__(data)
