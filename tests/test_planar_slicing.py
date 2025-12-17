from pathlib import Path

from compas.datastructures import Mesh

from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path as SlicerPath
from compas_slicer.slicers import PlanarSlicer

DATA_PATH = Path(__file__).parent / "tests_data"

compas_mesh = Mesh.from_obj(DATA_PATH / "cylinder.obj")
layer_height = 15.0

z = [compas_mesh.vertex_attribute(key, "z") for key in compas_mesh.vertices()]
min_z, max_z = min(z), max(z)
d = abs(min_z - max_z)
no_of_layers = int(d / layer_height) + 1


def test_planar_slicing_success():
    """Tests simple planar slicing."""
    slicer = PlanarSlicer(compas_mesh, layer_height=layer_height)
    slicer.slice_model()

    assert isinstance(slicer.layers, list), "The layers are not a list"
    print(len(slicer.layers))
    assert len(slicer.layers) == no_of_layers, "Wrong number of generated layers"
    assert isinstance(slicer.layers[0], Layer), "The slicer does not contain layers of type 'compas_slicer.Layer'"
    for i in range(len(slicer.layers)):
        assert len(slicer.layers[i].paths) == 1, "There is a layer with empty Contours list at index %d" % i
        assert isinstance(slicer.layers[i].paths[0], SlicerPath), "Wrong class type in Layer.Contour list"
        assert slicer.layers[i].paths[0].is_closed, (
            "Path resulting from slicing of cylinder using 'planar_compas' is open. It should be closed "
        )


if __name__ == "__main__":
    pass
