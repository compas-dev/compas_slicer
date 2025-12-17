from __future__ import annotations

from abc import abstractmethod
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING, Any

import numpy as np
from compas.geometry import (
    Vector,
    cross_vectors,
    distance_point_point,
    norm_vector,
    normalize_vector,
    scale_vector,
    subtract_vectors,
)
from compas.itertools import pairwise
from loguru import logger

from compas_slicer.config import GcodeConfig
from compas_slicer.geometry import PrintPointsCollection
from compas_slicer.print_organization.print_organization_utilities.gcode import create_gcode_text
from compas_slicer.slicers.base_slicer import BaseSlicer

if TYPE_CHECKING:
    from compas_slicer.geometry import Path, PrintPoint


__all__ = ["BasePrintOrganizer"]


class BasePrintOrganizer:
    """Base class for organizing the printing process.

    This class is meant to be extended for implementing various print organizers.
    Do not use this class directly. Use PlanarPrintOrganizer or InterpolationPrintOrganizer.

    Attributes
    ----------
    slicer : BaseSlicer
        An instance of a slicer class.
    printpoints : PrintPointsCollection
        Collection of printpoints organized by layer and path.

    """

    def __init__(self, slicer: BaseSlicer) -> None:
        if not isinstance(slicer, BaseSlicer):
            raise TypeError(f"slicer must be BaseSlicer, not {type(slicer)}")
        logger.info("Print Organizer")
        self.slicer = slicer
        self.printpoints = PrintPointsCollection()

    def __repr__(self) -> str:
        return "<BasePrintOrganizer>"

    @abstractmethod
    def create_printpoints(self) -> None:
        """To be implemented by inheriting classes."""
        pass

    def printpoints_iterator(self) -> Generator[PrintPoint, None, None]:
        """Iterate over all printpoints.

        Yields
        ------
        PrintPoint
            Each printpoint in the organizer.

        """
        if not self.printpoints.layers:
            raise ValueError("No printpoints have been created.")
        yield from self.printpoints.iter_printpoints()

    def printpoints_indices_iterator(self) -> Iterator[tuple[PrintPoint, int, int, int]]:
        """Iterate over printpoints with their indices.

        Yields
        ------
        tuple[PrintPoint, int, int, int]
            Printpoint, layer index, path index, printpoint index.

        """
        if not self.printpoints.layers:
            raise ValueError("No printpoints have been created.")
        yield from self.printpoints.iter_with_indices()

    @property
    def number_of_printpoints(self) -> int:
        """Total number of printpoints."""
        return self.printpoints.number_of_printpoints

    @property
    def number_of_paths(self) -> int:
        """Total number of paths."""
        return self.printpoints.number_of_paths

    @property
    def number_of_layers(self) -> int:
        """Number of layers."""
        return self.printpoints.number_of_layers

    @property
    def total_length_of_paths(self) -> float:
        """Total length of all paths (ignores extruder toggle)."""
        total_length = 0.0
        for layer in self.printpoints:
            for path in layer:
                for prev, curr in pairwise(path):
                    total_length += distance_point_point(prev.pt, curr.pt)
        return total_length

    @property
    def total_print_time(self) -> float | None:
        """Total print time if velocity is defined, else None."""
        if self.printpoints[0][0][0].velocity is None:
            return None

        total_time = 0.0
        for layer in self.printpoints:
            for path in layer:
                for prev, curr in pairwise(path):
                    length = distance_point_point(prev.pt, curr.pt)
                    total_time += length / curr.velocity
        return total_time

    def number_of_paths_on_layer(self, layer_index: int) -> int:
        """Number of paths within a layer."""
        return len(self.printpoints[layer_index])

    def remove_duplicate_points_in_path(self, layer_idx: int, path_idx: int, tolerance: float = 0.0001) -> None:
        """Remove subsequent points within a threshold distance.

        Parameters
        ----------
        layer_idx : int
            The layer index.
        path_idx : int
            The path index.
        tolerance : float
            Distance threshold for duplicate detection.

        """
        dup_index = []
        duplicate_ppts = []

        path = self.printpoints[layer_idx][path_idx]
        for i, printpoint in enumerate(path.printpoints[:-1]):
            next_ppt = path.printpoints[i + 1]
            if np.linalg.norm(np.array(printpoint.pt) - np.array(next_ppt.pt)) < tolerance:
                dup_index.append(i)
                duplicate_ppts.append(printpoint)

        if duplicate_ppts:
            logger.warning(
                f"Attention! {len(duplicate_ppts)} Duplicate printpoint(s) on "
                f"layer {layer_idx}, path {path_idx}, indices: {dup_index}. They will be removed."
            )
            for ppt in duplicate_ppts:
                path.printpoints.remove(ppt)

    def get_printpoint_neighboring_items(self, layer_idx: int, path_idx: int, i: int) -> list[PrintPoint | None]:
        """Get neighboring printpoints.

        Parameters
        ----------
        layer_idx : int
            The layer index.
        path_idx : int
            The path index.
        i : int
            Index of current printpoint.

        Returns
        -------
        list[PrintPoint | None]
            Previous and next printpoints (None if at boundary).

        """
        path = self.printpoints[layer_idx][path_idx]
        prev_pt = path[i - 1] if i > 0 else None
        next_pt = path[i + 1] if i < len(path) - 1 else None
        return [prev_pt, next_pt]

    def printout_info(self) -> None:
        """Print information about the PrintOrganizer."""
        ppts_attributes = {key: str(type(val)) for key, val in self.printpoints[0][0][0].attributes.items()}

        logger.info("---- PrintOrganizer Info ----")
        logger.info(f"Number of layers: {self.number_of_layers}")
        logger.info(f"Number of paths: {self.number_of_paths}")
        logger.info(f"Number of PrintPoints: {self.number_of_printpoints}")
        logger.info("PrintPoints attributes: ")
        for key, val in ppts_attributes.items():
            logger.info(f"     {key} : {val}")
        logger.info(f"Toolpath length: {self.total_length_of_paths:.0f} mm")

        print_time = self.total_print_time
        if print_time:
            minutes, sec = divmod(print_time, 60)
            hour, minutes = divmod(minutes, 60)
            logger.info(f"Total print time: {int(hour)} hours, {int(minutes)} minutes, {int(sec)} seconds")
        else:
            logger.info("Print Velocity has not been assigned, thus print time is not calculated.")

    def get_printpoint_up_vector(self, path: Path, k: int, normal: Vector) -> Vector:
        """Get printpoint up-vector orthogonal to path direction and normal.

        Parameters
        ----------
        path : Path
            The path containing the point.
        k : int
            Index of the point in path.points.
        normal : Vector
            The normal vector.

        Returns
        -------
        Vector
            The up vector.

        """
        p = path.points[k]
        if k < len(path.points) - 1:
            negative = False
            other_pt = path.points[k + 1]
        else:
            negative = True
            other_pt = path.points[k - 1]

        diff = normalize_vector(subtract_vectors(p, other_pt))
        up_vec = normalize_vector(cross_vectors(normal, diff))

        if negative:
            up_vec = scale_vector(up_vec, -1.0)
        if norm_vector(up_vec) == 0:
            up_vec = Vector(0, 0, 1)

        return Vector(*up_vec)

    def output_printpoints_dict(self) -> dict[int, dict[str, Any]]:
        """Create a flattened printpoints dictionary.

        Returns
        -------
        dict
            Flattened printpoints data for JSON serialization.

        """
        data = {}
        count = 0

        for i, layer in enumerate(self.printpoints):
            for j, path in enumerate(layer):
                self.remove_duplicate_points_in_path(i, j)
                for printpoint in path:
                    data[count] = printpoint.to_data()
                    count += 1

        logger.info(f"Generated {count} print points")
        return data

    def output_nested_printpoints_dict(self) -> dict[str, dict[str, dict[int, dict[str, Any]]]]:
        """Create a nested printpoints dictionary.

        Returns
        -------
        dict
            Nested printpoints data for JSON serialization.

        """
        data: dict[str, dict[str, dict[int, dict[str, Any]]]] = {}
        count = 0

        for i, layer in enumerate(self.printpoints):
            layer_key = f"layer_{i}"
            data[layer_key] = {}
            for j, path in enumerate(layer):
                path_key = f"path_{j}"
                data[layer_key][path_key] = {}
                self.remove_duplicate_points_in_path(i, j)
                for k, printpoint in enumerate(path):
                    data[layer_key][path_key][k] = printpoint.to_data()
                    count += 1

        logger.info(f"Generated {count} print points")
        return data

    def output_gcode(self, config: GcodeConfig | None = None) -> str:
        """Generate G-code text.

        Parameters
        ----------
        config : GcodeConfig | None
            G-code configuration. If None, uses defaults.

        Returns
        -------
        str
            G-code text.

        """
        return create_gcode_text(self, config)

    def get_printpoints_attribute(self, attr_name: str) -> list[Any]:
        """Get a list of attribute values from all printpoints.

        Parameters
        ----------
        attr_name : str
            Name of the attribute.

        Returns
        -------
        list
            Attribute values from all printpoints.

        """
        attr_values = []
        for pp in self.printpoints.iter_printpoints():
            if attr_name not in pp.attributes:
                raise KeyError(f"Attribute '{attr_name}' not in printpoint.attributes")
            attr_values.append(pp.attributes[attr_name])
        return attr_values

    # Legacy compatibility: provide printpoints_dict property that builds the old dict format
    @property
    def printpoints_dict(self) -> dict[str, dict[str, list[PrintPoint]]]:
        """Legacy accessor for the old dict format. Prefer using self.printpoints directly."""
        result: dict[str, dict[str, list[PrintPoint]]] = {}
        for i, layer in enumerate(self.printpoints):
            layer_key = f"layer_{i}"
            result[layer_key] = {}
            for j, path in enumerate(layer):
                path_key = f"path_{j}"
                result[layer_key][path_key] = list(path.printpoints)
        return result
