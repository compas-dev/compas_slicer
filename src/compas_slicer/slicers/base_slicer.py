import compas
import compas_slicer
from compas.datastructures import Mesh
from compas_slicer.utilities import utils
from compas.geometry import Polyline
from compas_slicer.geometry import Layer, VerticalLayer
from compas_slicer.post_processing import seams_align, unify_paths_orientation
import logging
import copy
from abc import abstractmethod

logger = logging.getLogger('logger')

__all__ = ['BaseSlicer']


class BaseSlicer(object):
    """
    This is an organizational class that holds all the information for the slice process.
    Do not use this class directly in your python code. Instead use PlanarSlicer or CurvedSlicer.
    This class is meant to be extended for the implementation of the various slicers.
    See :class:`compas.slicer.slicers.PlanarSlicer` and :class:`compas.slicer.slicers.CurvedSlicer` as examples.

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
        self.layers = []  # any class inheriting from SortedPathCollection, i.e.  Layer(horizontal sorting)
        # or VerticalLayer (vertical sorting)

        self.brim_toggle = False
        self.number_of_brim_paths = 0

    @property
    def total_number_of_points(self):
        """int: Total number of points in the slicer."""
        total_number_of_pts = 0
        for layer in self.layers:
            for path in layer.paths:
                total_number_of_pts += len(path.points)
        return total_number_of_pts

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

        #  --- Align the seams between layers and unify orientation
        seams_align(self, align_with='x_axis')
        unify_paths_orientation(self)

        logger.info("Created %d Layers with %d total number of points"
                    % (len(self.layers), self.total_number_of_points))

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

    ##############################
    #  --- Output

    def printout_info(self):
        """Prints out information from the slicing process."""

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
        """Visualizes slicing result using compas.viewers.

        Parameters
        ----------
        viewer: :class:`compas_viewers.objectviewer.Objectviewer`
            An instance of the Objectviewer class.
        visualize_mesh: bool, optional
            True to visualize mesh, False to not.
        visualize_paths: bool, optional
            True to visualize paths, False to not.
        """

        if visualize_mesh:
            viewer.add(self.mesh, settings={'color': '#ff0000',
                                            'opacity': 0.4, })

        if visualize_paths:
            for i, layer in enumerate(self.layers):
                for j, path in enumerate(layer.paths):
                    pts = copy.deepcopy(path.points)
                    if path.is_closed:
                        pts.append(pts[0])
                    polyline = Polyline(pts)
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
        if layers_data['0']['layer_type'] == 'horizontal_layer':
            slicer.layers = [Layer.from_data(layers_data[key]) for key in layers_data]
        else:  # 'vertical_layer'
            slicer.layers = [VerticalLayer.from_data(layers_data[key]) for key in layers_data]
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
            The slicers's data.

        """
        data = {'layers': self.get_layers_dict(),
                'mesh': self.mesh.to_data(),
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
