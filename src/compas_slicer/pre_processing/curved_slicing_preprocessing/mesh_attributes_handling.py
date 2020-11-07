import compas_slicer.utilities as utils
from compas.geometry import Point, distance_point_point_sqrd

__all__ = ['create_mesh_boundary_attributes',
           'get_existing_cut_indices',
           'get_existing_boundary_indices',
           'get_vertices_that_belong_to_cuts',
           'save_vertex_attributes',
           'restore_mesh_attributes',
           'replace_mesh_vertex_attribute']


def create_mesh_boundary_attributes(mesh, low_boundary_vs, high_boundary_vs):
    """
    Creates a default vertex attribute data['boundary']=0. Then it gives the value 1 to the vertices that belong
    to the lower boundary, and the value 2 to the vertices that belong to the higher boundary.
    """
    mesh.update_default_vertex_attributes({'boundary': 0})
    for vkey, data in mesh.vertices(data=True):
        if vkey in low_boundary_vs:
            data['boundary'] = 1
        elif vkey in high_boundary_vs:
            data['boundary'] = 2


###############################################
# --- Mesh existing attributes on vertices

def get_existing_cut_indices(mesh):
    """
    Returns
    ----------
        list, int.
        The cut indices (data['cut']>0) that exist on the mesh vertices.
    """
    cut_indices = []
    for vkey, data in mesh.vertices(data=True):
        if data['cut'] > 0:
            if data['cut'] not in cut_indices:
                cut_indices.append(data['cut'])
    cut_indices = sorted(cut_indices)
    return cut_indices


def get_existing_boundary_indices(mesh):
    """
    Returns
    ----------
        list, int.
        The boundary indices (data['boundary']>0) that exist on the mesh vertices.
    """
    indices = []
    for vkey, data in mesh.vertices(data=True):
        if data['boundary'] > 0:
            if data['boundary'] not in indices:
                indices.append(data['boundary'])
    boundary_indices = sorted(indices)
    return boundary_indices


def get_vertices_that_belong_to_cuts(mesh, cut_indices):
    """
    Returns
    ----------
        dict, key: int, the index of each cut
              value: list, the points that belong to this cut
    """
    cuts_dict = {i: [] for i in cut_indices}

    for vkey, data in mesh.vertices(data=True):
        if data['cut'] > 0:
            cut_index = data['cut']
            cuts_dict[cut_index].append(mesh.vertex_coordinates(vkey))

    for cut_index in cuts_dict:
        cuts_dict[cut_index] = utils.point_list_to_dict(cuts_dict[cut_index])

    return cuts_dict


###############################################
# --- Save and restore attributes

def save_vertex_attributes(mesh):
    """
    Saves the boundary and cut attributes that are on the mesh on a dictionary.
    """
    v_attributes_dict = {'boundary_1': [], 'boundary_2': [], 'cut': {}}

    cut_indices = []
    for vkey, data in mesh.vertices(data=True):
        cut_index = data['cut']
        if cut_index not in cut_indices:
            cut_indices.append(cut_index)
    cut_indices = sorted(cut_indices)

    for cut_index in cut_indices:
        v_attributes_dict['cut'][cut_index] = []

    for vkey, data in mesh.vertices(data=True):
        if data['boundary'] == 1:
            v_coords = mesh.vertex_coordinates(vkey)
            pt = Point(x=v_coords[0], y=v_coords[1], z=v_coords[2])
            v_attributes_dict['boundary_1'].append(pt)
        elif data['boundary'] == 2:
            v_coords = mesh.vertex_coordinates(vkey)
            pt = Point(x=v_coords[0], y=v_coords[1], z=v_coords[2])
            v_attributes_dict['boundary_2'].append(pt)
        if data['cut'] > 0:
            cut_index = data['cut']
            v_coords = mesh.vertex_coordinates(vkey)
            pt = Point(x=v_coords[0], y=v_coords[1], z=v_coords[2])
            v_attributes_dict['cut'][cut_index].append(pt)
    return v_attributes_dict


def restore_mesh_attributes(mesh, v_attributes_dict):
    """
    Restores the cut and boundary attributes on the mesh vertices from the dictionary of the previously saved attributes
    """
    mesh.update_default_vertex_attributes({'boundary': 0})
    mesh.update_default_vertex_attributes({'cut': 0})

    D_THRESHOLD = 0.01

    welded_mesh_vertices = []
    indices_to_vkeys = {}
    for i, vkey in enumerate(mesh.vertices()):
        v_coords = mesh.vertex_coordinates(vkey)
        pt = Point(x=v_coords[0], y=v_coords[1], z=v_coords[2])
        welded_mesh_vertices.append(pt)
        indices_to_vkeys[i] = vkey

    for v_coords in v_attributes_dict['boundary_1']:
        closest_index = utils.get_closest_pt_index(pt=v_coords, pts=welded_mesh_vertices)
        c_vkey = indices_to_vkeys[closest_index]
        if distance_point_point_sqrd(v_coords, mesh.vertex_coordinates(c_vkey)) < D_THRESHOLD:
            mesh.vertex_attribute(c_vkey, 'boundary', value=1)

    for v_coords in v_attributes_dict['boundary_2']:
        closest_index = utils.get_closest_pt_index(pt=v_coords, pts=welded_mesh_vertices)
        c_vkey = indices_to_vkeys[closest_index]
        if distance_point_point_sqrd(v_coords, mesh.vertex_coordinates(c_vkey)) < D_THRESHOLD:
            mesh.vertex_attribute(c_vkey, 'boundary', value=2)

    for cut_index in v_attributes_dict['cut']:
        for v_coords in v_attributes_dict['cut'][cut_index]:
            closest_index = utils.get_closest_pt_index(pt=v_coords, pts=welded_mesh_vertices)
            c_vkey = indices_to_vkeys[closest_index]
            if distance_point_point_sqrd(v_coords, mesh.vertex_coordinates(c_vkey)) < D_THRESHOLD:
                mesh.vertex_attribute(c_vkey, 'cut', value=int(cut_index))


def replace_mesh_vertex_attribute(mesh, old_attr, old_val, new_attr, new_val):
    """
    Replaces one vertex attribute with a new one. For all the vertices where data[old_attr]=old_val, then the
    old_val is replaced with 0, and data[new_attr]=new_val.
    """
    for vkey, data in mesh.vertices(data=True):
        if data[old_attr] == old_val:
            mesh.vertex_attribute(vkey, old_attr, 0)
            mesh.vertex_attribute(vkey, new_attr, new_val)


if __name__ == "__main__":
    pass
