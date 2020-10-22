import numpy as np
import logging
from compas_slicer.utilities import TerminalCommand
from compas.plugins import PluginNotInstalledError
packages = TerminalCommand('conda list').get_split_output_strings()
if 'igl' in packages:
    import igl


logger = logging.getLogger('logger')

__all__ = ['get_igl_EXACT_geodesic_distances',
           'get_custom_HEAT_geodesic_distances']


def get_igl_EXACT_geodesic_distances(mesh, vertices_start):
    """
    Docstring to be added.

    Attributes
    ----------
    xx : xx
        xx
    xx : xx
        xx
    """
    
    if 'igl' not in packages:
        raise PluginNotInstalledError("--------ATTENTION! ----------- \
                        Libigl library is missing! \
                        Install it with 'conda install -c conda-forge igl'")
    v, f = mesh.to_vertices_and_faces()
    v = np.array(v)
    f = np.array(f)
    vertices_target = np.arange(len(v))  # all vertices are targets
    vstart = np.array(vertices_start)
    distances = igl.exact_geodesic(v, f, vstart, vertices_target)
    return distances


def get_custom_HEAT_geodesic_distances(mesh, vi_sources, DATA_PATH,
                                       anisotropic_scaling, equalized_v_indices):
    raise NotImplementedError
