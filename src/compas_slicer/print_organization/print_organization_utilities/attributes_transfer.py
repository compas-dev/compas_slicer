from compas.geometry import closest_point_in_cloud, closest_point_on_plane, barycentric_coordinates

__all__ = ['transfer_mesh_attributes_to_point']


def is_reserved_attribute(attr):
    """ Returns True if the attribute name is a reserved, false otherwise. """
    taken_attributes = ['x', 'y', 'z',
                        'scalar_field']
    return attr in taken_attributes


def transfer_mesh_attributes_to_point(mesh, point):
    """
    It projects the point on the closest face of the mesh. Then if finds
    all the vertex and face attributes of the face and its attributes and transfers them to the point.
    The vertex attributes are transferred using barycentric coordinates.

    Parameters
    ----------
    mesh: compas.datastructures.Mesh
    point: 'compas.geometry.Point

    Returns
    -------
    dict that contains all the attributes
    """
    # project point on mesh
    f_centers = [mesh.face_centroid(fkey) for fkey in mesh.faces()]
    f_closest = closest_point_in_cloud(point, f_centers)[2]
    pt, vec = mesh.face_plane(f_closest)
    projection = closest_point_on_plane(point, (pt, vec))

    # get face attributes
    face_attrs = mesh.face_attributes(f_closest)
    keys_to_remove = [attr for attr in face_attrs if is_reserved_attribute(attr)]
    for key in keys_to_remove:
        del face_attrs[key]  # remove from face_attrs dictionary

    # get vertex attributes using barycentric coordinates
    vs = mesh.face_vertices(f_closest)
    bar_coords = barycentric_coordinates(projection, triangle=(mesh.vertex_coordinates(vs[0]),
                                                               mesh.vertex_coordinates(vs[1]),
                                                               mesh.vertex_coordinates(vs[2])))
    vertex_attrs = {}
    for attr in mesh.vertex_attributes(vs[0]):
        if not is_reserved_attribute(attr):
            vertex_attrs[attr] = 0
            vertex_attrs[attr] += bar_coords[0] * mesh.vertex_attributes(vs[0])[attr]
            vertex_attrs[attr] += bar_coords[1] * mesh.vertex_attributes(vs[1])[attr]
            vertex_attrs[attr] += bar_coords[2] * mesh.vertex_attributes(vs[2])[attr]

    vertex_attrs.update(face_attrs)  # merge two dictionaries
    return vertex_attrs
