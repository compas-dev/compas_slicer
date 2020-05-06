import pytest
import os
import compas
from compas.datastructures import Mesh

from compas_am.slicing.planar_slicing import create_planar_contours_meshcut
from compas_am.slicing.planar_slicing import create_planar_contours_numpy
from compas_am.slicing.printpath import Contour

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FILE = os.path.abspath(os.path.join(DATA, 'vase.obj'))

mesh = Mesh.from_obj(os.path.join(DATA, FILE))

def test_planar_contours_numpy():
    layer_height = 5
    result = create_planar_contours_numpy(mesh, layer_height)

    assert isinstance(result, list)
    assert len(result) >= layer_height
    assert isinstance(result[0], Contour)


def test_planar_contours_meshcut():
    layer_height = 5
    result = create_planar_contours_numpy(mesh, layer_height)

    assert isinstance(result, list)
    assert len(result) >= layer_height
    assert isinstance(result[0], Contour)