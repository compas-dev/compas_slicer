import os
from compas.datastructures import Mesh
from compas_am.slicing import Slicer

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FILE = os.path.abspath(os.path.join(DATA, 'branches_70_short.obj'))

compas_mesh = Mesh.from_obj(FILE)
slicer = Slicer(compas_mesh, slicer_type="planar_meshcut", layer_height=10.0)
slicer.slice_model(create_contours=True, create_infill=False, create_supports=False)


def test_polyline_simplification_curvature():
    pass  # TODO
    ## check if fitness is improving
