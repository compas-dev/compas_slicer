from __future__ import annotations

from typing import TYPE_CHECKING

from compas.geometry import Point
from loguru import logger

import compas_slicer
from compas_slicer.geometry import Layer, Path
from compas_slicer.post_processing.seams_align import seams_align

# Try CGAL first, fall back to pyclipper
_USE_CGAL = False
try:
    from compas_cgal.straight_skeleton_2 import offset_polygon as _cgal_offset
    from compas_cgal.straight_skeleton_2 import offset_polygon_with_holes as _cgal_offset_with_holes
    _USE_CGAL = True
except ImportError:
    _cgal_offset = None
    _cgal_offset_with_holes = None

if TYPE_CHECKING:
    from compas_slicer.slicers import BaseSlicer


__all__ = ['generate_brim', 'offset_polygon', 'offset_polygon_with_holes']


def _offset_polygon_cgal(points: list[Point], offset: float, z: float) -> list[Point]:
    """Offset a polygon using CGAL straight skeleton.

    Parameters
    ----------
    points : list[Point]
        2D/3D points of the polygon (z ignored for offset, restored after).
    offset : float
        Offset distance (positive = outward, negative = inward).
    z : float
        Z coordinate to assign to result points.

    Returns
    -------
    list[Point]
        Offset polygon points with z coordinate.
    """
    # CGAL expects points with z=0 and normal pointing up
    pts_2d = [[p[0], p[1], 0] for p in points]

    # CGAL offset: negative = inward, positive = outward (opposite of pyclipper)
    # For brim we want outward offset
    result_polys = _cgal_offset(pts_2d, -offset)

    if not result_polys:
        return []

    # Take first result polygon, add z coordinate
    result_pts = [Point(p[0], p[1], z) for p in result_polys[0].points]

    # Close the polygon
    if result_pts and result_pts[0] != result_pts[-1]:
        result_pts.append(result_pts[0])

    return result_pts


def _offset_polygon_pyclipper(points: list[Point], offset: float, z: float) -> list[Point]:
    """Offset a polygon using pyclipper.

    Parameters
    ----------
    points : list[Point]
        2D/3D points of the polygon.
    offset : float
        Offset distance (positive = outward).
    z : float
        Z coordinate to assign to result points.

    Returns
    -------
    list[Point]
        Offset polygon points with z coordinate.
    """
    import pyclipper
    from pyclipper import scale_from_clipper, scale_to_clipper

    SCALING_FACTOR = 2 ** 32

    xy_coords = [[p[0], p[1]] for p in points]

    pco = pyclipper.PyclipperOffset()
    pco.AddPath(
        scale_to_clipper(xy_coords, SCALING_FACTOR),
        pyclipper.JT_MITER,
        pyclipper.ET_CLOSEDPOLYGON
    )

    result = scale_from_clipper(pco.Execute(offset * SCALING_FACTOR), SCALING_FACTOR)

    if not result:
        return []

    result_pts = [Point(xy[0], xy[1], z) for xy in result[0]]

    # Close the polygon
    if result_pts:
        result_pts.append(result_pts[0])

    return result_pts


def offset_polygon(points: list[Point], offset: float, z: float) -> list[Point]:
    """Offset a polygon, using CGAL if available.

    Parameters
    ----------
    points : list[Point]
        Points of the polygon.
    offset : float
        Offset distance (positive = outward).
    z : float
        Z coordinate for result points.

    Returns
    -------
    list[Point]
        Offset polygon points.
    """
    if _USE_CGAL:
        return _offset_polygon_cgal(points, offset, z)
    else:
        return _offset_polygon_pyclipper(points, offset, z)


def offset_polygon_with_holes(
    outer: list[Point],
    holes: list[list[Point]],
    offset: float,
    z: float
) -> list[tuple[list[Point], list[list[Point]]]]:
    """Offset a polygon with holes using CGAL straight skeleton.

    Parameters
    ----------
    outer : list[Point]
        Points of the outer boundary (CCW orientation).
    holes : list[list[Point]]
        List of hole polygons (CW orientation).
    offset : float
        Offset distance (positive = outward, negative = inward).
    z : float
        Z coordinate for result points.

    Returns
    -------
    list[tuple[list[Point], list[list[Point]]]]
        List of (outer_boundary, holes) tuples for resulting polygons.

    Raises
    ------
    ImportError
        If CGAL is not available.
    """
    if not _USE_CGAL:
        raise ImportError("offset_polygon_with_holes requires compas_cgal")

    from compas.geometry import Polygon

    # CGAL expects Polygon objects with z=0, normal up for outer, down for holes
    outer_poly = Polygon([[p[0], p[1], 0] for p in outer])
    hole_polys = [Polygon([[p[0], p[1], 0] for p in hole]) for hole in holes]

    # CGAL: negative = outward, positive = inward (opposite of our convention)
    result = _cgal_offset_with_holes(outer_poly, hole_polys, -offset)

    # Convert back to Points with z coordinate
    output = []
    for poly, poly_holes in result:
        outer_pts = [Point(p[0], p[1], z) for p in poly.points]
        if outer_pts and outer_pts[0] != outer_pts[-1]:
            outer_pts.append(outer_pts[0])

        hole_pts_list = []
        for hole in poly_holes:
            hole_pts = [Point(p[0], p[1], z) for p in hole.points]
            if hole_pts and hole_pts[0] != hole_pts[-1]:
                hole_pts.append(hole_pts[0])
            hole_pts_list.append(hole_pts)

        output.append((outer_pts, hole_pts_list))

    return output


def generate_brim(slicer: BaseSlicer, layer_width: float, number_of_brim_offsets: int) -> None:
    """Creates a brim around the bottom contours of the print.

    Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.PlanarSlicer`
        An instance of the compas_slicer.slicers.PlanarSlicer class
    layer_width: float
        A number representing the distance between brim contours
        (typically the width of a layer)
    number_of_brim_offsets: int
        Number of brim paths to add.
    """
    backend = "CGAL" if _USE_CGAL else "pyclipper"
    logger.info(f"Generating brim with layer width: {layer_width:.2f} mm, {number_of_brim_offsets} offsets ({backend})")

    if slicer.layers[0].is_raft:
        raise NameError("Raft found: cannot apply brim when raft is used, choose one")

    # (1) --- find if slicer has vertical or horizontal layers, and select which paths are to be offset.
    if isinstance(slicer.layers[0], compas_slicer.geometry.VerticalLayer):  # Vertical layers
        # then find all paths that lie on the print platform and make them brim.
        paths_to_offset, layers_i = slicer.find_vertical_layers_with_first_path_on_base()
        for i, first_path in zip(layers_i, paths_to_offset):
            slicer.layers[i].paths.remove(first_path)  # remove first path that will become part of the brim layer
        has_vertical_layers = True

    else:  # Horizontal layers
        # then replace the first layer with a brim layer.
        paths_to_offset = slicer.layers[0].paths
        has_vertical_layers = False

    assert len(paths_to_offset) > 0, 'Attention the brim generator did not find any path on the base. Please check the \
                                      paths of your slicer. '

    # (2) --- create new empty brim_layer
    brim_layer = Layer(paths=[])
    brim_layer.is_brim = True
    brim_layer.number_of_brim_offsets = number_of_brim_offsets

    # (3) --- create offsets and add them to the paths of the brim_layer
    for path in paths_to_offset:
        z = path.points[0][2]

        for i in range(number_of_brim_offsets):
            offset_distance = i * layer_width
            offset_pts = offset_polygon(path.points, offset_distance, z)

            if offset_pts:
                new_path = Path(points=offset_pts, is_closed=True)
                brim_layer.paths.append(new_path)

    brim_layer.paths.reverse()  # go from outside towards the object
    brim_layer.calculate_z_bounds()

    # (4) --- Add the brim layer to the slicer
    if not has_vertical_layers:
        slicer.layers[0] = brim_layer  # replace first layer
    else:
        slicer.layers.insert(0, brim_layer)  # insert brim layer as the first layer of the slicer

    seams_align(slicer, align_with="next_path")


if __name__ == "__main__":
    pass
