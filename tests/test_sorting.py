import pytest
import os
from compas.datastructures import Mesh

from compas_am.slicing.printpath import Contour
from compas_am.slicing.slicer import Slicer

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FILE = os.path.abspath(os.path.join(DATA, 'branches_70_short.obj'))

compas_mesh = Mesh.from_obj(FILE)
slicer = Slicer(compas_mesh, slicer_type = "planar_meshcut", layer_height = 10.0)
slicer.slice_model(create_contours = True, create_infill = False, create_supports = False)

def test_sort_shortest_path():
    pass #TODO

def test_sort_per_segment():
    slicer.sort_paths(method = "per_segment")
    assert len(slicer.sorted_paths) == 70, "Sorting per segment returned wrong number of segments"
    for i,segment in enumerate(slicer.sorted_paths):
        assert len(segment.contours) > 0 , "The Segment at index %d has no contours"%i
        assert isinstance(segment.contours[0], Contour ),  "Wrong class type in Segment.Contour list"