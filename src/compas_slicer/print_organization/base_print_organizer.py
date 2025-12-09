from __future__ import annotations

import logging
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

from compas_slicer.print_organization.print_organization_utilities.gcode import create_gcode_text
from compas_slicer.slicers.base_slicer import BaseSlicer

if TYPE_CHECKING:
    from compas_slicer.geometry import Path, PrintPoint

logger = logging.getLogger("logger")

__all__ = ["BasePrintOrganizer"]

# Type alias for the nested printpoints dictionary
PrintPointsDict = dict[str, dict[str, list["PrintPoint"]]]


class BasePrintOrganizer:
    """Base class for organizing the printing process.

    This class is meant to be extended for implementing various print organizers.
    Do not use this class directly. Use PlanarPrintOrganizer or InterpolationPrintOrganizer.

    Attributes
    ----------
    slicer : BaseSlicer
        An instance of a slicer class.
    printpoints_dict : PrintPointsDict
        Nested dictionary of printpoints organized by layer and path.

    """

    def __init__(self, slicer: BaseSlicer) -> None:
        if not isinstance(slicer, BaseSlicer):
            raise TypeError(f"slicer must be BaseSlicer, not {type(slicer)}")
        logger.info("Print Organizer")
        self.slicer = slicer
        self.printpoints_dict: PrintPointsDict = {}

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
        if not self.printpoints_dict:
            raise ValueError("No printpoints have been created.")
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                yield from self.printpoints_dict[layer_key][path_key]

    def printpoints_indices_iterator(self) -> Iterator[tuple[PrintPoint, int, int, int]]:
        """Iterate over printpoints with their indices.

        Yields
        ------
        tuple[PrintPoint, int, int, int]
            Printpoint, layer index, path index, printpoint index.

        """
        if not self.printpoints_dict:
            raise ValueError("No printpoints have been created.")
        for i, layer_key in enumerate(self.printpoints_dict):
            for j, path_key in enumerate(self.printpoints_dict[layer_key]):
                for k, printpoint in enumerate(self.printpoints_dict[layer_key][path_key]):
                    yield printpoint, i, j, k

    @property
    def number_of_printpoints(self) -> int:
        """Total number of printpoints."""
        return sum(
            len(self.printpoints_dict[layer_key][path_key])
            for layer_key in self.printpoints_dict
            for path_key in self.printpoints_dict[layer_key]
        )

    @property
    def number_of_paths(self) -> int:
        """Total number of paths."""
        return sum(len(self.printpoints_dict[layer_key]) for layer_key in self.printpoints_dict)

    @property
    def number_of_layers(self) -> int:
        """Number of layers."""
        return len(self.printpoints_dict)

    @property
    def total_length_of_paths(self) -> float:
        """Total length of all paths (ignores extruder toggle)."""
        total_length = 0.0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for prev, curr in pairwise(self.printpoints_dict[layer_key][path_key]):
                    total_length += distance_point_point(prev.pt, curr.pt)
        return total_length

    @property
    def total_print_time(self) -> float | None:
        """Total print time if velocity is defined, else None."""
        if self.printpoints_dict["layer_0"]["path_0"][0].velocity is None:
            return None

        total_time = 0.0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for prev, curr in pairwise(self.printpoints_dict[layer_key][path_key]):
                    length = distance_point_point(prev.pt, curr.pt)
                    total_time += length / curr.velocity
        return total_time

    def number_of_paths_on_layer(self, layer_index: int) -> int:
        """Number of paths within a layer."""
        return len(self.printpoints_dict[f"layer_{layer_index}"])

    def remove_duplicate_points_in_path(
        self, layer_key: str, path_key: str, tolerance: float = 0.0001
    ) -> None:
        """Remove subsequent points within a threshold distance.

        Parameters
        ----------
        layer_key : str
            The layer key.
        path_key : str
            The path key.
        tolerance : float
            Distance threshold for duplicate detection.

        """
        dup_index = []
        duplicate_ppts = []

        path_points = self.printpoints_dict[layer_key][path_key]
        for i, printpoint in enumerate(path_points[:-1]):
            next_ppt = path_points[i + 1]
            if np.linalg.norm(np.array(printpoint.pt) - np.array(next_ppt.pt)) < tolerance:
                dup_index.append(i)
                duplicate_ppts.append(printpoint)

        if duplicate_ppts:
            logger.warning(
                f"Attention! {len(duplicate_ppts)} Duplicate printpoint(s) on "
                f"{layer_key}, {path_key}, indices: {dup_index}. They will be removed."
            )
            for ppt in duplicate_ppts:
                self.printpoints_dict[layer_key][path_key].remove(ppt)

    def get_printpoint_neighboring_items(
        self, layer_key: str, path_key: str, i: int
    ) -> list[PrintPoint | None]:
        """Get neighboring printpoints.

        Parameters
        ----------
        layer_key : str
            The layer key.
        path_key : str
            The path key.
        i : int
            Index of current printpoint.

        Returns
        -------
        list[PrintPoint | None]
            Previous and next printpoints (None if at boundary).

        """
        path_points = self.printpoints_dict[layer_key][path_key]
        prev_pt = path_points[i - 1] if i > 0 else None
        next_pt = path_points[i + 1] if i < len(path_points) - 1 else None
        return [prev_pt, next_pt]

    def printout_info(self) -> None:
        """Print information about the PrintOrganizer."""
        ppts_attributes = {
            key: str(type(val))
            for key, val in self.printpoints_dict["layer_0"]["path_0"][0].attributes.items()
        }

        print("\n---- PrintOrganizer Info ----")
        print(f"Number of layers: {self.number_of_layers}")
        print(f"Number of paths: {self.number_of_paths}")
        print(f"Number of PrintPoints: {self.number_of_printpoints}")
        print("PrintPoints attributes: ")
        for key, val in ppts_attributes.items():
            print(f"     {key} : {val}")
        print(f"Toolpath length: {self.total_length_of_paths:.0f} mm")

        print_time = self.total_print_time
        if print_time:
            minutes, sec = divmod(print_time, 60)
            hour, minutes = divmod(minutes, 60)
            print(f"Total print time: {int(hour)} hours, {int(minutes)} minutes, {int(sec)} seconds")
        else:
            print("Print Velocity has not been assigned, thus print time is not calculated.")
        print("")

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

        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                self.remove_duplicate_points_in_path(layer_key, path_key)
                for printpoint in self.printpoints_dict[layer_key][path_key]:
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

        for layer_key in self.printpoints_dict:
            data[layer_key] = {}
            for path_key in self.printpoints_dict[layer_key]:
                data[layer_key][path_key] = {}
                self.remove_duplicate_points_in_path(layer_key, path_key)
                for i, printpoint in enumerate(self.printpoints_dict[layer_key][path_key]):
                    data[layer_key][path_key][i] = printpoint.to_data()
                    count += 1

        logger.info(f"Generated {count} print points")
        return data

    def output_gcode(self, parameters: dict[str, Any]) -> str:
        """Generate G-code text.

        Parameters
        ----------
        parameters : dict
            G-code generation parameters.

        Returns
        -------
        str
            G-code text.

        """
        return create_gcode_text(self, parameters)

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
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for ppt in self.printpoints_dict[layer_key][path_key]:
                    if attr_name not in ppt.attributes:
                        raise KeyError(f"Attribute '{attr_name}' not in printpoint.attributes")
                    attr_values.append(ppt.attributes[attr_name])
        return attr_values
