from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Any, Callable

import progressbar
from compas.geometry import Plane, Point
from compas.plugins import PluginNotInstalledError

from compas_slicer.geometry import Layer, Path

if TYPE_CHECKING:
    from compas.datastructures import Mesh


__all__ = ['create_planar_paths']


def create_planar_paths(mesh: Mesh, planes: list[Plane]) -> list[Layer]:
    """Creates planar contours very efficiently using CGAL.

    Parameters
    ----------
    mesh: :class: 'compas.datastructures.Mesh'
        A compas mesh.
    planes: list, :class: 'compas.geometry.Plane'
    """
    try:
        from compas_cgal.slicer import slice_mesh
    except ImportError as e:
        raise PluginNotInstalledError(
            "Compas_cgal library is missing! "
            "You can't use this planar slicing method without it. "
            "Install it with: pip install compas_cgal"
        ) from e

    # prepare mesh for slicing
    M = mesh.to_vertices_and_faces()

    # slicing operation
    contours = slice_mesh(M, planes)
    cgal_layers = get_grouped_list(contours, key_function=key_function)

    layers = []
    with progressbar.ProgressBar(max_value=len(planes)) as bar:
        for i, layer in enumerate(cgal_layers):
            paths_per_layer = []
            for path in layer:
                points_per_contour = []
                for point in path:
                    pt = Point(point[0], point[1], point[2])
                    points_per_contour.append(pt)

                # check if path is closed
                if points_per_contour[0] == points_per_contour[-1]:
                    is_closed = True
                else:
                    is_closed = False
                # generate paths
                path = Path(points=points_per_contour, is_closed=is_closed)
                paths_per_layer.append(path)

            # generate layers
            layer = Layer(paths_per_layer)
            layers.append(layer)

            # advance progressbar
            bar.update(i)

    return layers


def get_grouped_list(
    item_list: list[Any], key_function: Callable[[Any], Any]
) -> list[list[Any]]:
    """ Groups layers horizontally. """
    # first sort, because grouping only groups consecutively matching items
    sorted_list = sorted(item_list, key=key_function)
    # group items, using the provided key function
    grouped_iter = itertools.groupby(sorted_list, key_function)
    # return reformatted list
    return [list(group) for _key, group in grouped_iter]


def key_function(item: list[list[float]]) -> float:
    return item[0][2]


if __name__ == "__main__":
    pass
