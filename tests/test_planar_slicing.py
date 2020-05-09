import pytest
import warnings
import os
from compas.datastructures import Mesh

from compas_am.slicing.planar_slicing import create_planar_contours_meshcut
from compas_am.slicing.planar_slicing import create_planar_contours_numpy
from compas_am.slicing.printpath import Layer, Contour

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FILE = os.path.abspath(os.path.join(DATA, 'vase.obj'))

mesh = Mesh.from_obj(os.path.join(DATA, FILE))

z = [mesh.vertex_attribute(key, 'z') for key in mesh.vertices()]
z_bounds = max(z) - min(z)

def test_planar_contours_meshcut():
    layer_height = 20
    layers = create_planar_contours_meshcut(mesh, layer_height)

    assert isinstance(layers, list), "The method does not return a list"
    assert len(layers) >= z_bounds/layer_height, "Insufficient number of contours"
    assert isinstance(layers[0], Layer), "The method does not return items of type 'compas_am.Layer'"
    for i in range(len(layers)):
        assert len(layers[i].contours) >=0 , "There is a layer with empty Contours list at index %d"%i
        assert isinstance(layers[i].contours[0], Contour ), "Wrong class type in Layer.Contour list"

def test_planar_contours_numpy():
    layer_height = 20
    layers = create_planar_contours_numpy(mesh, layer_height)

    assert isinstance(layers, list), "The method does not return a list"
    assert len(layers) >= z_bounds/layer_height, "Insufficient number of contours"
    assert isinstance(layers[0], Layer), "The method does not return items of type 'compas_am.Layer'"
    for i in range(len(layers)):
        assert len(layers[i].contours) >=0 , "There is a layer with empty Contours list at index %d"%i
        assert isinstance(layers[i].contours[0], Contour ),  "Wrong class type in Layer.Contour list"