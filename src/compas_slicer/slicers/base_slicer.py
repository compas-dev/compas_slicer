import compas
import compas_slicer
from compas_slicer.utilities import utils
from compas.geometry import Polyline
from compas_slicer.geometry import Layer, VerticalLayer
from compas_slicer.post_processing import seams_align, unify_paths_orientation
import time
import logging

logger = logging.getLogger('logger')

__all__ = ['BaseSlicer']


class BaseSlicer(object):
    """
    Slicer class is an organizational class that holds all the information for the slice process
    This class is meant to be extended for the implementation of the various slicers.
    See PlanarSlicer and Curved slicer as examples

    Attributes
    ----------
    mesh : compas.datastructures.Mesh
        Input mesh, it must be a triangular mesh (i.e. no quads or n-gons allowed)
    """

    def __init__(self, mesh):
        #  check input
        assert isinstance(mesh, compas.datastructures.Mesh), \
            "Input mesh must be of type <compas.datastructures.Mesh>, not " + str(type(mesh))
        utils.check_triangular_mesh(mesh)

        #  input
        self.mesh = mesh
        logger.info("Input Mesh with : %d vertices, %d Faces"
                    % (len(list(self.mesh.vertices())), len(list(self.mesh.faces()))))

        self.layer_height = None
        self.layers = []  # any class inheriting from SortedPathCollection, i.e.  Layer(horizontal sorting)
        # or VerticalLayer (vertical sorting)

    @property
    def total_number_of_points(self):
        total_number_of_pts = 0
        for layer in self.layers:
            for path in layer.paths:
                total_number_of_pts += len(path.points)
        return total_number_of_pts

    @property
    def vertical_layers(self):
        if len(self.layers) > 0:
            if isinstance(self.layers[0], VerticalLayer):
                return self.layers  # What a hacky way to do this...
            else:
                raise NameError('The slicer does not have vertical_layers')
        else:
            return []

    ##############################
    #  --- Functions

    def slice_model(self, *args, **kwargs):
        start_time = time.time()  # time measurement
        self.generate_paths()
        end_time = time.time()
        logger.info('')
        logger.info("Slicing operation took: %.2f seconds" % (end_time - start_time))
        self.post_processing()

    def generate_paths(self):
        # To be implemented by the inheriting classes
        raise NotImplementedError

    def post_processing(self):
        #  --- Align the seams between layers and unify orientation
        seams_align(self, align_with='x_axis')
        unify_paths_orientation(self)

        logger.info("Created %d Layers with %d total number of points"
                    % (len(self.layers), self.total_number_of_points))

    ##############################
    #  --- Output

    def printout_info(self):
        open_paths = 0
        closed_paths = 0
        total_number_of_pts = 0
        number_of_path_collections = 0

        for layer in self.layers:
            number_of_path_collections += 1
            for path in layer.paths:
                total_number_of_pts += len(path.points)
                if path.is_closed:
                    closed_paths += 1
                else:
                    open_paths += 1

        print("\n---- Slicer Info ----")
        print("Number of layers: %d" % number_of_path_collections)
        print("Number of paths: %d, open paths: %d, closed paths: %d" % (
            open_paths + closed_paths, open_paths, closed_paths))
        print("Number of sampling printpoints on layers: %d" % total_number_of_pts)
        print("")

    def visualize_on_viewer(self, viewer, visualize_mesh=False, visualize_paths=True):
        if visualize_mesh:
            viewer.add(self.mesh, settings={'color': '#ff0000',
                                            'opacity': 0.4, })

        if visualize_paths:
            for i, layer in enumerate(self.layers):
                for j, path in enumerate(layer.paths):
                    polyline = Polyline(path.points)
                    if isinstance(layer, compas_slicer.geometry.VerticalLayer):
                        viewer.add(polyline, name="VerticalSegment %d, Path %d" % (i, j),
                                   settings={'color': '#ffffff'})
                    else:
                        viewer.add(polyline, name="Layer %d, Path %d" % (i, j),
                                   settings={'color': '#ffffff'})

    ##############################
    #  --- To data, from data

    @classmethod
    def from_data(cls, data):
        mesh = compas.datastructures.Mesh.from_data(data['mesh'])
        slicer = cls(mesh)
        layers_data = data['layers']
        slicer.layers = [Layer.from_data(layers_data[key]) for key in layers_data]
        slicer.layer_height = data['layer_height']
        return slicer

    def to_json(self, filepath, name):
        utils.save_to_json(self.to_data(), filepath, name)

    def to_data(self):
        data = {'layers': self.get_layers_dict(),
                'mesh': self.mesh.to_data(),
                'layer_height': self.layer_height}
        return data

    def get_layers_dict(self):
        data = {}
        for i, layer in enumerate(self.layers):
            data[i] = layer.to_data()
        return data


if __name__ == "__main__":
    pass
