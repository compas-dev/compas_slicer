import compas
import numpy as np
from compas.datastructures import Mesh
from compas_slicer.utilities import utils
from compas_slicer.geometry import Layer, VerticalLayer
from compas_slicer.post_processing import seams_align
from compas_slicer.post_processing import unify_paths_orientation
import logging
from abc import abstractmethod
from compas.datastructures import mesh_bounding_box
from compas.geometry import distance_point_point_sqrd

logger = logging.getLogger('logger')

__all__ = ['BaseSlicer']


class BaseSlicer(object):
    """
    This is an organizational class that holds all the information for the slice process.
    Do not use this class directly in your python code. Instead use PlanarSlicer or InterpolationSlicer.
    This class is meant to be extended for the implementation of the various slicers.
    See :class:`compas.slicer.slicers.PlanarSlicer` and :class:`compas.slicer.slicers.InterpolationSlicer` as examples.

    Attributes
    ----------
    mesh: :class:`compas.datastructures.Mesh`
        Input mesh, has to be a triangular mesh (i.e. no quads or n-gons allowed)
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
        self.layers = []  # any class inheriting from Layer(horizontal sorting)

    ##############################
    #  --- Properties

    @property
    def number_of_points(self):
        """ Returns int: Total number of points in the slicer."""
        total_number_of_pts = 0
        for layer in self.layers:
            for path in layer.paths:
                total_number_of_pts += len(path.points)
        return total_number_of_pts

    @property
    def number_of_layers(self):
        """ Returns int: Total number of layers."""
        return len(self.layers)

    @property
    def number_of_paths(self):
        """ Returns tuple (int, int, int): Total number of paths, number of open paths, number of closed paths. """
        total_number_of_paths = 0
        closed_paths = 0
        open_paths = 0
        for layer in self.layers:
            total_number_of_paths += len(layer.paths)
            for path in layer.paths:
                if path.is_closed:
                    closed_paths += 1
                else:
                    open_paths += 1

        return total_number_of_paths, closed_paths, open_paths

    @property
    def vertical_layers(self):
        """ Returns a list of all the vertical layers stored in the slicer. """
        return [layer for layer in self.layers if isinstance(layer, VerticalLayer)]

    @property
    def horizontal_layers(self):
        """ Returns a list of all the layers stored in the slicer that are NOT vertical. """
        return [layer for layer in self.layers if not isinstance(layer, VerticalLayer)]

    ##############################
    #  --- Functions

    def slice_model(self, *args, **kwargs):
        """Slices the model and applies standard post-processing and removing of invalid paths."""

        self.generate_paths()
        self.remove_invalid_paths_and_layers()
        self.post_processing()

    @abstractmethod
    def generate_paths(self):
        """To be implemented by the inheriting classes. """
        pass

    def post_processing(self):
        """Applies standard post-processing operations: seams_align and unify_paths."""
        self.close_paths()

        #  --- Align the seams between layers and unify orientation
        seams_align(self, align_with='next_path')
        unify_paths_orientation(self)

        self.close_paths()
        logger.info("Created %d Layers with %d total number of points" % (len(self.layers), self.number_of_points))

    def close_paths(self):
        """ For paths that are labeled as closed, it makes sure that the first and the last point are identical. """
        for layer in self.layers:
            for path in layer.paths:
                if path.is_closed:  # if the path is closed, first and last point should be the same.
                    if distance_point_point_sqrd(path.points[0], path.points[-1]) > 0.00001:  # if not already the same
                        path.points.append(path.points[0])

    def remove_invalid_paths_and_layers(self):
        """Removes invalid layers and paths from the slicer."""

        paths_to_remove = []
        layers_to_remove = []

        for i, layer in enumerate(self.layers):
            for j, path in enumerate(layer.paths):
                # check if a path has less than two points and appends to list to_remove
                if len(path.points) < 2:
                    paths_to_remove.append(path)
                    logger.warning("Invalid Path found: Layer %d, Path %d, %s" % (i, j, str(path)))
                    # check if the layer that the invalid path was in has only one path
                    # this means that path is now invalid, and the entire layer should be removed
                    if len(layer.paths) == 1:
                        layers_to_remove.append(layer)
                        logger.warning("Invalid Layer found: Layer %d, %s" % (i, str(layer)))
            # check for layers with less than one path and appends to list to_remove
            if len(layer.paths) < 1:
                layers_to_remove.append(layer)
                logger.warning("Invalid Layer found: Layer %d, %s" % (i, str(layer)))

        # compares the two lists and removes any invalid items
        for i, layer in enumerate(self.layers):
            for j, path in enumerate(layer.paths):
                if path in paths_to_remove:
                    layer.paths.remove(path)
            if layer in layers_to_remove:
                self.layers.remove(layer)

    def find_vertical_layers_with_first_path_on_base(self):
        bbox = mesh_bounding_box(self.mesh)
        z_min = min([p[2] for p in bbox])
        paths_on_base = []
        vertical_layer_indices = []
        d_threshold = 30

        for i, vertical_layer in enumerate(self.vertical_layers):
            first_path = vertical_layer.paths[0]
            avg_z_dist_from_min = np.average(np.array([abs(pt[2] - z_min) for pt in first_path.points]))

            if avg_z_dist_from_min < d_threshold:
                paths_on_base.append(vertical_layer.paths[0])
                vertical_layer_indices.append(i)

        return paths_on_base, vertical_layer_indices

    ##############################
    #  --- Output

    def printout_info(self):
        """Prints out information from the slicing process."""
        no_of_paths, closed_paths, open_paths = self.number_of_paths

        print("\n---- Slicer Info ----")
        print("Number of layers: %d" % self.number_of_layers)
        print("Number of paths: %d, open paths: %d, closed paths: %d" % (no_of_paths, open_paths, closed_paths))
        print("Number of sampling printpoints on layers: %d" % self.number_of_points)
        print("")

    ##############################
    #  --- To data, from data

    @classmethod
    def from_data(cls, data):
        """Construct a slicer from its data representation.

        Parameters
        ----------
        data: dict
            The data dictionary.

        Returns
        -------
        layer
            The constructed slicer.

        """
        mesh = Mesh.from_data(data['mesh'])
        slicer = cls(mesh)
        layers_data = data['layers']
        for layer_key in layers_data:
            if layers_data[layer_key]['layer_type'] == 'horizontal_layer':
                slicer.layers.append(Layer.from_data(layers_data[layer_key]))
            else:  # 'vertical_layer'
                slicer.layers.append(VerticalLayer.from_data(layers_data[layer_key]))
        slicer.layer_height = data['layer_height']
        return slicer

    def to_json(self, filepath, name):
        """Writes the slicer to a JSON file."""
        utils.save_to_json(self.to_data(), filepath, name)

    def to_data(self):
        """Returns a dictionary of structured data representing the data structure.

        Returns
        -------
        dict
            The slicer's data.

        """
        # To avoid errors when saving to Json, create a copy of the self.mesh and remove from it
        # any non-serializable attributes (by checking a random face and a random vertex, assuming
        # that all faces and vertices share the same types of attributes).
        mesh = self.mesh.copy()
        v_key = mesh.get_any_vertex()
        v_attrs = mesh.vertex_attributes(v_key)
        for attr_key in v_attrs:
            if not utils.is_jsonable(v_attrs[attr_key]):
                logger.error('vertex : ' + attr_key + str(v_attrs[attr_key]))
                for v in mesh.vertices():
                    mesh.unset_vertex_attribute(v, attr_key)

        f_key = mesh.get_any_face()
        f_attrs = mesh.face_attributes(f_key)
        for attr_key in f_attrs:
            if not utils.is_jsonable(f_attrs[attr_key]):
                logger.error('face : ' + attr_key, f_attrs[attr_key])
                mesh.update_default_face_attributes({attr_key: 0.0})  # just set all to 0.0

        # fill data dictionary with slicer info
        data = {'layers': self.get_layers_dict(),
                'mesh': mesh.to_data(),
                'layer_height': self.layer_height}
        return data

    def get_layers_dict(self):
        """Returns a dictionary consisting of the layers.
        """
        data = {}
        for i, layer in enumerate(self.layers):
            data[i] = layer.to_data()
        return data


if __name__ == "__main__":
    pass
