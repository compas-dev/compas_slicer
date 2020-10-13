from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path
import os
from compas.datastructures import Mesh
from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path
import os
from compas.datastructures import Mesh
from compas.geometry import Point, Frame

from compas_slicer.utilities import save_to_json
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.functionality import generate_brim
from compas_slicer.functionality import spiralize_contours
from compas_slicer.functionality import seams_align
from compas_slicer.functionality import seams_smooth, unify_paths_orientation
from compas_slicer.fabrication import RoboticPrintOrganizer
from compas_slicer.fabrication import RobotPrinter
from compas_viewers.objectviewer import ObjectViewer
from compas_slicer.functionality import move_mesh_to_point, simplify_paths_rdp
import time

DATA = os.path.join(os.path.dirname(__file__), '..', 'data/test_geometries')
FILE = os.path.abspath(os.path.join(DATA, 'cylinder.obj'))

compas_mesh = Mesh.from_obj(os.path.join(DATA, FILE))
layer_height = 10.0

z = [compas_mesh.vertex_attribute(key, 'z') for key in compas_mesh.vertices()]
min_z, max_z = min(z), max(z)
d = abs(min_z - max_z)
no_of_layers = int(d / layer_height) + 1


def test_planar_contours():
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_compas", layer_height=layer_height)
    slicer.slice_model()

    assert isinstance(slicer.layers, list), "The layers are not a list"
    print(len(slicer.layers))
    # assert len(slicer.layers) == no_of_layers, "Wrong number of generated layers"
    assert isinstance(slicer.layers[0], Layer), "The slicer does not contain layers of type 'compas_slicer.Layer'"
    for i in range(len(slicer.layers)):
        assert len(slicer.layers[i].paths) == 1, "There is a layer with empty Contours list at index %d" % i
        assert isinstance(slicer.layers[i].paths[0], Path), "Wrong class type in Layer.Contour list"
        assert slicer.layers[i].paths[0].is_closed, "Path resulting from slicing of cylinder using 'planar_compas' is " \
                                                    "open. It should be closed "

z = [compas_mesh.vertex_attribute(key, 'z') for key in compas_mesh.vertices()]
min_z, max_z = min(z), max(z)
d = abs(min_z - max_z)
no_of_layers = int(d / layer_height)

def test_planar_contours_cgal():
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_cgal", layer_height=layer_height)
    slicer.slice_model()

    assert isinstance(slicer.layers, list), "The layers are not a list"
    print(len(slicer.layers))
    # assert len(slicer.layers) == no_of_layers, "Wrong number of generated layers"
    assert isinstance(slicer.layers[0], Layer), "The slicer does not contain layers of type 'compas_slicer.Layer'"
    for i in range(len(slicer.layers)):
        assert len(slicer.layers[i].paths) == 1, "There is a layer with empty Contours list at index %d" % i
        assert isinstance(slicer.layers[i].paths[0], Path), "Wrong class type in Layer.Contour list"
        assert slicer.layers[i].paths[0].is_closed, "Path resulting from slicing of cylinder using 'planar_cgal' is " \
                                                    "open. It should be closed "

    assert isinstance(slicer.layers, list), "The layers are not a list"
    print(len(slicer.layers))
    assert len(slicer.layers) == no_of_layers, "Wrong number of generated layers"
    assert isinstance(slicer.layers[0], Layer), "The slicer does not contain layers of type 'compas_slicer.Layer'"
    for i in range(len(slicer.layers)):
        assert len(slicer.layers[i].paths) == 1, "There is a layer with empty Contours list at index %d" % i
        assert isinstance(slicer.layers[i].paths[0], Path), "Wrong class type in Layer.Contour list"
        assert slicer.layers[i].paths[0].is_closed, "Path resulting from slicing of cylinder using 'planar_compas' is " \
                                                    "open. It should be closed "

if __name__ == '__main__':
    pass
    # test_planar_contours()

    test_planar_contours_cgal()
    print('Done!')