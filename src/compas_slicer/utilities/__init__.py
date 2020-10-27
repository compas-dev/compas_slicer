"""
********************************************************************************
utilities
********************************************************************************

.. currentmodule:: compas_slicer.utilities


utils
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    save_to_json
    load_from_json
    get_average_point
    total_length_of_dictionary
    flattened_list_of_dictionary
    interrupt
    point_list_to_dict
    get_closest_mesh_normal_to_pt
    get_closest_pt_index
    get_closest_pt
    plot_networkx_graph
    get_mesh_vertex_coords_with_attribute
    get_dict_key_from_value
    get_closest_mesh_normal_to_pt
    smooth_vectors
    get_normal_of_path_on_xy_plane


geodesics
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    get_igl_EXACT_geodesic_distances
    get_custom_HEAT_geodesic_distances

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .utils import *  # noqa: F401 E402 F403
from .terminal_command import *  # noqa: F401 E402 F403

__all__ = [name for name in dir() if not name.startswith('_')]
