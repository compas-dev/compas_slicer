from compas.geometry import barycentric_coordinates
import logging
import progressbar
from compas_slicer.utilities.utils import pull_pts_to_mesh_faces

logger = logging.getLogger('logger')


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

    all_pts = []
    for layer_key in printpoints_dict:
        for path_key in printpoints_dict[layer_key]:
            for ppt in printpoints_dict[layer_key][path_key]:
                all_pts.append(ppt.pt)

    closest_fks, projected_pts = pull_pts_to_mesh_faces(mesh, all_pts)

    i = 0
    with progressbar.ProgressBar(max_value=len(all_pts)) as bar:
        for layer_key in printpoints_dict:
            for path_key in printpoints_dict[layer_key]:
                for ppt in printpoints_dict[layer_key][path_key]:
                    fkey = closest_fks[i]
                    proj_pt = projected_pts[i]
                    ppt.attributes = transfer_mesh_attributes_to_point(mesh, fkey, proj_pt)
                    i += 1
                    bar.update(i)


def is_reserved_attribute(attr):
    """ Returns True if the attribute name is a reserved, false otherwise. """
    taken_attributes = ['x', 'y', 'z', 'uv',
                        'scalar_field']
    return attr in taken_attributes


def transfer_mesh_attributes_to_point(mesh, fkey, proj_pt):
    """
    It projects the point on the closest face of the mesh. Then if finds
    all the vertex and face attributes of the face and its attributes and transfers them to the point.
    The vertex attributes are transferred using barycentric coordinates.

    Parameters
    ----------
    mesh: compas.datastructures.Mesh
    fkey: face key
    proj_pt: list [x,y,z], point projected on the plane of the face fkey

    Returns
    -------
    dict that contains all the attributes that correspond to the printpoints position
    """

    vs = mesh.face_vertices(fkey)
    bar_coords = barycentric_coordinates(proj_pt, triangle=(mesh.vertex_coordinates(vs[0]),
                                                            mesh.vertex_coordinates(vs[1]),
                                                            mesh.vertex_coordinates(vs[2])))

    # get face attributes
    face_attrs = mesh.face_attributes(fkey)
    keys_to_remove = [attr for attr in face_attrs if is_reserved_attribute(attr)]
    for key in keys_to_remove:
        del face_attrs[key]  # remove from face_attrs dictionary

    # get vertex attributes using barycentric coordinates
    vs = mesh.face_vertices(fkey)
    vertex_attrs = {}
    checked_attrs = []
    for attr in mesh.vertex_attributes(vs[0]):
        if not is_reserved_attribute(attr):
            if not (attr in checked_attrs):
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
