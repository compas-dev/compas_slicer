from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import scipy
from compas.geometry import (
    Point,
    Vector,
    closest_point_in_cloud,
    closest_point_on_plane,
    distance_point_point_sqrd,
    length_vector,
    normalize_vector,
)
from compas.plugins import PluginNotInstalledError
from loguru import logger

from compas_slicer.utilities.terminal_command import TerminalCommand

if TYPE_CHECKING:
    from compas.datastructures import Mesh
    from numpy.typing import NDArray
    from scipy.sparse import csr_matrix

    from compas_slicer.geometry import Path as SlicerPath
    from compas_slicer.geometry import PrintPoint, PrintPointsCollection


__all__ = ['remap',
           'remap_unbound',
           'get_output_directory',
           'save_to_json',
           'load_from_json',
           'is_jsonable',
           'get_jsonable_attributes',
           'save_to_text_file',
           'flattened_list_of_dictionary',
           'interrupt',
           'point_list_to_dict',
           'point_list_from_dict',
           'get_closest_mesh_vkey_to_pt',
           'get_mesh_cotmatrix',
           'get_mesh_cotans',
           'get_mesh_massmatrix',
           'get_mesh_cotmatrix_igl',
           'get_mesh_cotans_igl',
           'get_closest_pt_index',
           'get_closest_pt',
           'pull_pts_to_mesh_faces',
           'get_mesh_vertex_coords_with_attribute',
           'get_dict_key_from_value',
           'find_next_printpoint',
           'find_previous_printpoint',
           'smooth_vectors',
           'get_normal_of_path_on_xy_plane',
           'get_all_files_with_name',
           'get_closest_mesh_normal_to_pt',
           'check_package_is_installed']


def remap(input_val: float, in_from: float, in_to: float, out_from: float, out_to: float) -> float:
    """Bounded remap from source domain to target domain."""
    if input_val <= in_from:
        return out_from
    elif input_val >= in_to:
        return out_to
    else:
        return remap_unbound(input_val, in_from, in_to, out_from, out_to)


def remap_unbound(input_val: float, in_from: float, in_to: float, out_from: float, out_to: float) -> float:
    """Remap input_val from source domain to target domain (no clamping)."""
    out_range = out_to - out_from
    in_range = in_to - in_from
    in_val = input_val - in_from
    val = (float(in_val) / in_range) * out_range
    out_val = out_from + val
    return out_val


def get_output_directory(path: str | Path) -> Path:
    """Get or create 'output' directory in the given path.

    Parameters
    ----------
    path : str | Path
        The path where the 'output' directory will be created.

    Returns
    -------
    Path
        The path to the 'output' directory.

    """
    output_dir = Path(path) / 'output'
    output_dir.mkdir(exist_ok=True)
    return output_dir


def get_closest_pt_index(pt: Point | NDArray, pts: list[Point] | NDArray) -> int:
    """Find the index of the closest point to pt in pts.

    Parameters
    ----------
    pt : Point | NDArray
        Query point.
    pts : list[Point] | NDArray
        Point cloud to search.

    Returns
    -------
    int
        Index of the closest point.

    """
    ci: int = closest_point_in_cloud(point=pt, cloud=pts)[2]
    return ci


def get_closest_pt(pt: Point | NDArray, pts: list[Point]) -> Point:
    """Find the closest point to pt in pts.

    Parameters
    ----------
    pt : Point | NDArray
        Query point.
    pts : list[Point]
        Point cloud to search.

    Returns
    -------
    Point
        The closest point.

    """
    ci = closest_point_in_cloud(point=pt, cloud=pts)[2]
    return pts[ci]


def pull_pts_to_mesh_faces(mesh: Mesh, points: list[Point]) -> tuple[list[int], list[Point]]:
    """Project points to mesh and find their closest face keys.

    Parameters
    ----------
    mesh : Mesh
        The mesh to project onto.
    points : list[Point]
        Points to project.

    Returns
    -------
    tuple[list[int], list[Point]]
        Closest face keys and projected points.

    """
    points_arr = np.array(points, dtype=np.float64).reshape((-1, 3))
    fi_fk = dict(enumerate(mesh.faces()))
    f_centroids = np.array([mesh.face_centroid(fkey) for fkey in mesh.faces()], dtype=np.float64)
    closest_fis = np.argmin(scipy.spatial.distance_matrix(points_arr, f_centroids), axis=1)
    closest_fks = [fi_fk[fi] for fi in closest_fis]
    projected_pts = [closest_point_on_plane(point, mesh.face_plane(fi)) for point, fi in zip(points_arr, closest_fis)]
    return closest_fks, projected_pts


def smooth_vectors(vectors: list[Vector], strength: float, iterations: int) -> list[Vector]:
    """Smooth vectors iteratively.

    Parameters
    ----------
    vectors : list[Vector]
        Vectors to smooth.
    strength : float
        Smoothing strength (0-1).
    iterations : int
        Number of smoothing iterations.

    Returns
    -------
    list[Vector]
        Smoothed vectors.

    """
    for _ in range(iterations):
        for i, n in enumerate(vectors):
            if 0 < i < len(vectors) - 1:
                neighbors_average = (vectors[i - 1] + vectors[i + 1]) * 0.5
            else:
                neighbors_average = n
            vectors[i] = n * (1 - strength) + neighbors_average * strength
    return vectors


#######################################
#  json

def save_to_json(
    data: dict[str, Any] | dict[int, Any] | list[Any], filepath: str | Path, name: str
) -> None:
    """Save data to JSON file.

    Parameters
    ----------
    data : dict | list
        Data to save.
    filepath : str | Path
        Directory path.
    name : str
        Filename.

    """
    filename = Path(filepath) / name
    logger.info(f"Saving to json: {filename}")
    filename.write_text(json.dumps(data, indent=3, sort_keys=True))


def load_from_json(filepath: str | Path, name: str) -> Any:
    """Load data from JSON file.

    Parameters
    ----------
    filepath : str | Path
        Directory path.
    name : str
        Filename.

    Returns
    -------
    Any
        Loaded data.

    """
    filename = Path(filepath) / name
    data = json.loads(filename.read_text())
    logger.info(f"Loaded json: {filename}")
    return data


def is_jsonable(x: Any) -> bool:
    """Return True if x can be JSON-serialized."""
    try:
        json.dumps(x)
        return True
    except TypeError:
        return False


def get_jsonable_attributes(attributes_dict: dict[str, Any]) -> dict[str, Any]:
    """Convert attributes dict to JSON-serializable form."""
    jsonable_attr: dict[str, Any] = {}
    for attr_key in attributes_dict:
        attr = attributes_dict[attr_key]
        if is_jsonable(attr):
            jsonable_attr[attr_key] = attr
        else:
            if isinstance(attr, np.ndarray):
                jsonable_attr[attr_key] = list(attr)
            else:
                jsonable_attr[attr_key] = 'non serializable attribute'
    return jsonable_attr


#######################################
#  text file

def save_to_text_file(data: str, filepath: str | Path, name: str) -> None:
    """Save text to file.

    Parameters
    ----------
    data : str
        Text to save.
    filepath : str | Path
        Directory path.
    name : str
        Filename.

    """
    filename = Path(filepath) / name
    logger.info(f"Saving to text file: {filename}")
    filename.write_text(data)


#######################################
#  mesh utils

def check_triangular_mesh(mesh: Mesh) -> None:
    """Check if mesh is triangular, raise TypeError if not.

    Parameters
    ----------
    mesh : Mesh
        The mesh to check.

    Raises
    ------
    TypeError
        If any face is not a triangle.

    """
    for f_key in mesh.faces():
        vs = mesh.face_vertices(f_key)
        if len(vs) != 3:
            raise TypeError(f"Found quad at face {f_key}, vertices: {len(vs)}. Only triangular meshes supported.")


def get_closest_mesh_vkey_to_pt(mesh: Mesh, pt: Point) -> int:
    """Find the vertex key closest to the point.

    Parameters
    ----------
    mesh : Mesh
        The mesh.
    pt : Point
        Query point.

    Returns
    -------
    int
        Closest vertex key.

    """
    vertex_tupples = [(v_key, Point(data['x'], data['y'], data['z'])) for v_key, data in mesh.vertices(data=True)]
    vertex_tupples = sorted(vertex_tupples, key=lambda v_tupple: distance_point_point_sqrd(pt, v_tupple[1]))
    closest_vkey: int = vertex_tupples[0][0]
    return closest_vkey


def get_closest_mesh_normal_to_pt(mesh: Mesh, pt: Point) -> Vector:
    """Find the closest vertex normal to the point.

    Parameters
    ----------
    mesh : Mesh
        The mesh.
    pt : Point
        Query point.

    Returns
    -------
    Vector
        Normal at closest vertex.

    """
    closest_vkey = get_closest_mesh_vkey_to_pt(mesh, pt)
    v = mesh.vertex_normal(closest_vkey)
    return Vector(v[0], v[1], v[2])


def get_mesh_vertex_coords_with_attribute(mesh: Mesh, attr: str, value: Any) -> list[Point]:
    """Get coordinates of vertices where attribute equals value.

    Parameters
    ----------
    mesh : Mesh
        The mesh.
    attr : str
        Attribute name.
    value : Any
        Value to match.

    Returns
    -------
    list[Point]
        Points of matching vertices.

    """
    pts: list[Point] = []
    for vkey, data in mesh.vertices(data=True):
        if data[attr] == value:
            pts.append(Point(*mesh.vertex_coordinates(vkey)))
    return pts


def get_normal_of_path_on_xy_plane(k: int, point: Point, path: SlicerPath, mesh: Mesh) -> Vector:
    """Find the normal of the curve on xy plane at point with index k.

    Parameters
    ----------
    k : int
        Index of the point.
    point : Point
        The point.
    path : SlicerPath
        The path containing the point.
    mesh : Mesh
        The mesh (fallback for degenerate cases).

    Returns
    -------
    Vector
        Normal vector.

    """
    # find mesh normal is not really needed in the 2D case of planar slicer
    # instead we only need the normal of the curve based on the neighboring pts
    if (0 < k < len(path.points) - 1) or path.is_closed:
        prev_pt = path.points[k - 1]
        next_pt = path.points[(k + 1) % len(path.points)]
        v1 = np.array(normalize_vector(Vector.from_start_end(prev_pt, point)))
        v2 = np.array(normalize_vector(Vector.from_start_end(point, next_pt)))
        v = (v1 + v2) * 0.5
        normal = [-v[1], v[0], v[2]]  # rotate 90 degrees COUNTER-clockwise on the xy plane

    else:
        if k == 0:
            next_pt = path.points[k + 1]
            v = normalize_vector(Vector.from_start_end(point, next_pt))
            normal = [-v[1], v[0], v[2]]  # rotate 90 degrees COUNTER-clockwise on the xy plane
        else:  # k == len(path.points)-1:
            prev_pt = path.points[k - 1]
            v = normalize_vector(Vector.from_start_end(point, prev_pt))
            normal = [v[1], -v[0], v[2]]  # rotate 90 degrees clockwise on the xy plane

    if length_vector(normal) == 0:
        # When the neighboring elements happen to cancel out, then search for the true normal,
        # and project it on the xy plane for consistency
        normal = get_closest_mesh_normal_to_pt(mesh, point)
        normal = [normal[0], normal[1], 0]

    normal = normalize_vector(normal)
    normal = Vector(*list(normal))
    return normal


#######################################
# mesh matrix utils (NumPy implementations)

def get_mesh_cotmatrix(mesh: Mesh, fix_boundaries: bool = True) -> csr_matrix:
    """Get the cotangent Laplacian matrix of the mesh.

    Computes L_ij = (cot α_ij + cot β_ij) / 2 for adjacent vertices,
    with L_ii = -sum_j L_ij (row sum = 0).

    Parameters
    ----------
    mesh : Mesh
        The mesh (must be triangulated).
    fix_boundaries : bool
        If True, zero out rows for boundary vertices.

    Returns
    -------
    csr_matrix
        Sparse matrix (V x V), cotangent Laplacian.

    """
    V, F = mesh.to_vertices_and_faces()
    vertices = np.array(V, dtype=np.float64)
    faces = np.array(F, dtype=np.int32)

    n_vertices = len(vertices)

    # Get cotangent weights for each half-edge
    # For each face, compute cotangents of all three angles
    i0, i1, i2 = faces[:, 0], faces[:, 1], faces[:, 2]
    v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]

    # Edge vectors
    e0 = v2 - v1  # opposite to vertex 0
    e1 = v0 - v2  # opposite to vertex 1
    e2 = v1 - v0  # opposite to vertex 2

    # Cotangent of angle at vertex i = dot(e_j, e_k) / |cross(e_j, e_k)|
    # where e_j and e_k are edges adjacent to vertex i
    def cotangent(a: NDArray, b: NDArray) -> NDArray:
        cross = np.cross(a, b)
        cross_norm = np.linalg.norm(cross, axis=1)
        dot = np.sum(a * b, axis=1)
        # Avoid division by zero
        cross_norm = np.maximum(cross_norm, 1e-10)
        return dot / cross_norm

    # Cotangent at each vertex of each face
    cot0 = cotangent(-e2, e1)  # angle at vertex 0
    cot1 = cotangent(-e0, e2)  # angle at vertex 1
    cot2 = cotangent(-e1, e0)  # angle at vertex 2

    # Build sparse matrix
    # L_ij += 0.5 * cot(angle opposite to edge ij)
    row = np.concatenate([i0, i1, i1, i2, i2, i0])
    col = np.concatenate([i1, i0, i2, i1, i0, i2])
    data = np.concatenate([cot2, cot2, cot0, cot0, cot1, cot1]) * 0.5

    L = csr_matrix((data, (row, col)), shape=(n_vertices, n_vertices))

    # Make symmetric and set diagonal to negative row sum
    L = L + L.T
    L = L - scipy.sparse.diags(np.array(L.sum(axis=1)).flatten())

    if fix_boundaries:
        # Zero out rows for boundary vertices
        boundary_mask = np.zeros(n_vertices, dtype=bool)
        for i, (_vkey, vdata) in enumerate(mesh.vertices(data=True)):
            if vdata.get('boundary', 0) > 0:
                boundary_mask[i] = True

        if np.any(boundary_mask):
            L = L.tolil()
            for i in np.where(boundary_mask)[0]:
                L[i, :] = 0
            L = L.tocsr()

    return L


def get_mesh_cotans(mesh: Mesh) -> NDArray:
    """Get the cotangent entries of the mesh.

    Parameters
    ----------
    mesh : Mesh
        The mesh (must be triangulated).

    Returns
    -------
    NDArray
        F x 3 array of 1/2*cotangents for corresponding angles.
        Column i contains cotangent of angle at vertex i of each face.

    """
    V, F = mesh.to_vertices_and_faces()
    vertices = np.array(V, dtype=np.float64)
    faces = np.array(F, dtype=np.int32)

    i0, i1, i2 = faces[:, 0], faces[:, 1], faces[:, 2]
    v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]

    e0 = v2 - v1
    e1 = v0 - v2
    e2 = v1 - v0

    def cotangent(a: NDArray, b: NDArray) -> NDArray:
        cross = np.cross(a, b)
        cross_norm = np.linalg.norm(cross, axis=1)
        dot = np.sum(a * b, axis=1)
        cross_norm = np.maximum(cross_norm, 1e-10)
        return dot / cross_norm

    cot0 = cotangent(-e2, e1)
    cot1 = cotangent(-e0, e2)
    cot2 = cotangent(-e1, e0)

    return np.column_stack([cot0, cot1, cot2]) * 0.5


def get_mesh_massmatrix(mesh: Mesh) -> csr_matrix:
    """Get the mass matrix of the mesh (Voronoi area weights).

    Parameters
    ----------
    mesh : Mesh
        The mesh (must be triangulated).

    Returns
    -------
    csr_matrix
        Sparse diagonal matrix (V x V), vertex areas.

    """
    V, F = mesh.to_vertices_and_faces()
    vertices = np.array(V, dtype=np.float64)
    faces = np.array(F, dtype=np.int32)

    n_vertices = len(vertices)

    # Compute face areas
    i0, i1, i2 = faces[:, 0], faces[:, 1], faces[:, 2]
    v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]

    cross = np.cross(v1 - v0, v2 - v0)
    face_areas = 0.5 * np.linalg.norm(cross, axis=1)

    # Distribute 1/3 of each face area to each vertex
    vertex_areas = np.zeros(n_vertices)
    np.add.at(vertex_areas, i0, face_areas / 3)
    np.add.at(vertex_areas, i1, face_areas / 3)
    np.add.at(vertex_areas, i2, face_areas / 3)

    return scipy.sparse.diags(vertex_areas)


# Backwards compatibility aliases
get_mesh_cotmatrix_igl = get_mesh_cotmatrix
get_mesh_cotans_igl = get_mesh_cotans


#######################################
#  dict utils

def point_list_to_dict(pts_list: list[Point | Vector]) -> dict[int, list[float]]:
    """Convert list of points/vectors to dict for JSON.

    Parameters
    ----------
    pts_list : list[Point | Vector]
        List of points or vectors.

    Returns
    -------
    dict[int, list[float]]
        Dict mapping index to [x, y, z].

    """
    data: dict[int, list[float]] = {}
    for i in range(len(pts_list)):
        data[i] = list(pts_list[i])
    return data


def point_list_from_dict(data: dict[Any, list[float]]) -> list[list[float]]:
    """Convert dict of points to list of [x, y, z].

    Parameters
    ----------
    data : dict[Any, list[float]]
        Dict mapping keys to [x, y, z].

    Returns
    -------
    list[list[float]]
        List of [x, y, z] coordinates.

    """
    return [[data[i][0], data[i][1], data[i][2]] for i in data]


def flattened_list_of_dictionary(dictionary: dict[Any, list[Any]]) -> list[Any]:
    """Flatten dictionary values into a single list.

    Parameters
    ----------
    dictionary : dict[Any, list[Any]]
        Dictionary with list values.

    Returns
    -------
    list[Any]
        Flattened list.

    """
    flattened_list: list[Any] = []
    for key in dictionary:
        for item in dictionary[key]:
            flattened_list.append(item)
    return flattened_list


def get_dict_key_from_value(dictionary: dict[Any, Any], val: Any) -> Any:
    """Return the key of a dictionary that stores the value.

    Parameters
    ----------
    dictionary : dict
        The dictionary to search.
    val : Any
        Value to find.

    Returns
    -------
    Any
        The key, or "key doesn't exist" if not found.

    """
    for key in dictionary:
        value = dictionary[key]
        if val == value:
            return key
    return "key doesn't exist"


def find_next_printpoint(
    printpoints: PrintPointsCollection, i: int, j: int, k: int
) -> PrintPoint | None:
    """
    Returns the next printpoint from the current printpoint if it exists, otherwise returns None.

    Parameters
    ----------
    printpoints : PrintPointsCollection
        The collection of printpoints.
    i : int
        Layer index.
    j : int
        Path index.
    k : int
        Printpoint index within the path.

    Returns
    -------
    PrintPoint | None
        The next printpoint or None if at the end.

    """
    next_ppt = None
    if k < len(printpoints[i][j]) - 1:  # If there are more ppts in the current path
        next_ppt = printpoints[i][j][k + 1]
    else:
        if j < len(printpoints[i]) - 1:  # Otherwise take the next path
            next_ppt = printpoints[i][j + 1][0]
        else:
            if i < len(printpoints) - 1:  # Otherwise take the next layer
                next_ppt = printpoints[i + 1][0][0]
    return next_ppt


def find_previous_printpoint(
    printpoints: PrintPointsCollection, i: int, j: int, k: int
) -> PrintPoint | None:
    """
    Returns the previous printpoint from the current printpoint if it exists, otherwise returns None.

    Parameters
    ----------
    printpoints : PrintPointsCollection
        The collection of printpoints.
    i : int
        Layer index.
    j : int
        Path index.
    k : int
        Printpoint index within the path.

    Returns
    -------
    PrintPoint | None
        The previous printpoint or None if at the start.

    """
    prev_ppt = None
    if k > 0:  # If not the first point in a path
        prev_ppt = printpoints[i][j][k - 1]
    else:
        if j > 0:  # Otherwise take the last point of the previous path
            prev_ppt = printpoints[i][j - 1][-1]
        else:
            if i > 0:  # Otherwise take the last path of the previous layer
                prev_ppt = printpoints[i - 1][-1][-1]
    return prev_ppt


#######################################
#  control flow

def interrupt() -> None:
    """
    Interrupts the flow of the code while it is running.
    It asks for the user to press a enter to continue or abort.
    """
    value = input("Press enter to continue, Press 1 to abort ")
    if isinstance(value, str) and value == '1':
        raise ValueError("Aborted")


#######################################
#  load all files with name

def get_all_files_with_name(
    startswith: str, endswith: str, DATA_PATH: str | Path
) -> list[str]:
    """
    Finds all the filenames in the DATA_PATH that start and end with the provided strings

    Parameters
    ----------
    startswith: str
    endswith: str
    DATA_PATH: str | Path

    Returns
    ----------
    list[str]
        All the filenames
    """
    files = [f.name for f in Path(DATA_PATH).iterdir()
             if f.name.startswith(startswith) and f.name.endswith(endswith)]
    logger.info(f'Reloading: {files}')
    return files


#######################################
# check installation


def check_package_is_installed(package_name: str) -> None:
    """ Throws an error if igl python bindings are not installed in the current environment. """
    packages = TerminalCommand('conda list').get_split_output_strings()
    if package_name not in packages:
        raise PluginNotInstalledError(" ATTENTION! Package : " + package_name +
                                      " is missing! Please follow installation guide to install it.")


if __name__ == "__main__":
    pass
