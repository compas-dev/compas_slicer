from compas.geometry import closest_point_in_cloud, closest_point_on_plane, barycentric_coordinates
import logging

logger = logging.getLogger('logger')
import progressbar

__all__ = ['transfer_mesh_attributes_to_printpoints']


######################
# PrintPoints Attributes
######################

def transfer_mesh_attributes_to_printpoints(mesh, printpoints_dict):
    """
    Transfers face and vertex attributes from the mesh to the printpoints.
    Each printpoint is projected to the closest mesh face. It takes directly all the face attributes.
    It takes the averaged vertex attributes of the face vertices using barycentric coordinates.

    Face attributes can be anything.
    Vertex attributes can only be entities that support multiplication with a scalar. They have been tested to work
    with scalars and np.arrays.

    The reserved attribute names (see 'is_reserved_attribute(attr)') are not passed on to the printpoints.
    """
    logger.info('Transferring mesh attributes to the printpoints.')

    total_number_of_pts = 0
    for layer_key in printpoints_dict:
        for path_key in printpoints_dict[layer_key]:
            for _ in printpoints_dict[layer_key][path_key]:
                total_number_of_pts += 1

    count = 0
    with progressbar.ProgressBar(max_value=total_number_of_pts) as bar:
        for layer_key in printpoints_dict:
            for path_key in printpoints_dict[layer_key]:
                for ppt in printpoints_dict[layer_key][path_key]:
                    ppt.attributes = transfer_mesh_attributes_to_point(mesh, ppt.pt)
                    count += 1
                    bar.update(count)


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
    checked_attrs = []
    for attr in mesh.vertex_attributes(vs[0]):
        if not is_reserved_attribute(attr):
            if not(attr in checked_attrs):
                check_that_attribute_can_be_multiplied(attr, mesh.vertex_attributes(vs[0])[attr])
                checked_attrs.append(attr)
            vertex_attrs[attr] = 0
            vertex_attrs[attr] += bar_coords[0] * mesh.vertex_attributes(vs[0])[attr]
            vertex_attrs[attr] += bar_coords[1] * mesh.vertex_attributes(vs[1])[attr]
            vertex_attrs[attr] += bar_coords[2] * mesh.vertex_attributes(vs[2])[attr]

    vertex_attrs.update(face_attrs)  # merge two dictionaries
    return vertex_attrs


def check_that_attribute_can_be_multiplied(attr_name, value):
    try:
        value * 1.0
        return True
    except TypeError:
        raise ValueError('Attention! The following vertex attribute cannot be multiplied with a scalar. %s : %s '
                         % (attr_name, str(type(value))))
