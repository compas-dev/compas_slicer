import logging
import compas_slicer
import compas_slicer.utilities.utils as utils
import numpy as np
from compas_slicer.geometry import Path

logger = logging.getLogger('logger')

__all__ = ['Layer',
           'VerticalLayer',
           'VerticalLayersManager']


class Layer(object):
    """
    A Layer stores a group of ordered paths that are generated when a geometry is sliced.
    Layers are typically organized horizontally, but can also be organized vertically (see VerticalLayer).
    A Layer consists of one, or multiple Paths (depending on the geometry).

    Attributes
    ----------
    paths: list
        :class:`compas_slicer.geometry.Path`
    is_brim: bool
        True if this layer is a brim layer.
    number_of_brim_offsets: int
        The number of brim offsets this layer has (None if no brim).
    is_raft: bool
        True if this layer is a raft layer.
    """

    def __init__(self, paths):
        # check input
        if paths is None:
            paths = []
        if len(paths) > 0:
            assert isinstance(paths[0], compas_slicer.geometry.Path)
        self.paths = paths

        self.min_max_z_height = (None, None)  # Tuple containing the min and max z height of the layer.
        if paths:
            self.calculate_z_bounds()

        # brim
        self.is_brim = False
        self.number_of_brim_offsets = None

        # raft
        self.is_raft = False

    def __repr__(self):
        no_of_paths = len(self.paths) if self.paths else 0
        return "<Layer object with %i paths>" % no_of_paths

    @property
    def total_number_of_points(self):
        """Returns the total number of points within the layer."""
        num = 0
        for path in self.paths:
            num += len(path.printpoints)
        return num

    def calculate_z_bounds(self):
        """ Fills in the attribute self.min_max_z_height. """
        assert len(self.paths) > 0, "You cannot calculate z_bounds because the list of paths is empty."
        z_min = 2 ** 32  # very big number
        z_max = -2 ** 32  # very small number
        for path in self.paths:
            for pt in path.points:
                z_min = min(z_min, pt[2])
                z_max = max(z_max, pt[2])
        self.min_max_z_height = (z_min, z_max)

    @classmethod
    def from_data(cls, data):
        """Construct a layer from its data representation.

        Parameters
        ----------
        data: dict
            The data dictionary.

        Returns
        -------
        layer
            The constructed layer.
        """
        paths_data = data['paths']
        paths = [Path.from_data(paths_data[key]) for key in paths_data]
        layer = cls(paths=paths)
        layer.is_brim = data['is_brim']
        layer.number_of_brim_offsets = data['number_of_brim_offsets']
        layer.min_max_z_height = data['min_max_z_height']
        return layer

    def to_data(self):
        """Returns a dictionary of structured data representing the data structure.

        Returns
        -------
        dict
            The layer's data.
        """
        data = {'paths': {i: [] for i in range(len(self.paths))},
                'layer_type': 'horizontal_layer',
                'is_brim': self.is_brim,
                'number_of_brim_offsets': self.number_of_brim_offsets,
                'min_max_z_height': self.min_max_z_height}
        for i, path in enumerate(self.paths):
            data['paths'][i] = path.to_data()
        return data


class VerticalLayer(Layer):
    """
    Vertical ordering. A VerticalLayer stores the print paths sorted in vertical groups.
    It is created with an empty list of paths that is filled in afterwards.

    Attributes
    ----------
    id: int
        Identifier of vertical layer.
    """

    def __init__(self, id=0, paths=None):
        Layer.__init__(self, paths=paths)
        self.id = id
        self.head_centroid = None

    def __repr__(self):
        no_of_paths = len(self.paths) if self.paths else 0
        return "<Vertical Layer object with id : %d and %d paths>" % (self.id, no_of_paths)

    def append_(self, path):
        """ Add path to self.paths list. """
        self.paths.append(path)
        self.compute_head_centroid()
        self.calculate_z_bounds()

    def compute_head_centroid(self):
        """ Find the centroid of all the points of the last path in the self.paths list"""
        pts = np.array(self.paths[-1].points)
        self.head_centroid = np.mean(pts, axis=0)

    def printout_details(self):
        """ Prints the details of the class. """
        logger.info("VerticalLayer id : %d" % self.id)
        logger.info("Total number of paths : %d" % len(self.paths))

    def to_data(self):
        """Returns a dictionary of structured data representing the data structure.

        Returns
        -------
        dict
            The vertical layer's data.
        """
        data = {'paths': {i: [] for i in range(len(self.paths))},
                'min_max_z_height': self.min_max_z_height,
                'layer_type': 'vertical_layer'}
        for i, path in enumerate(self.paths):
            data['paths'][i] = path.to_data()
        return data

    @classmethod
    def from_data(cls, data):
        """Construct a vertical layer from its data representation.

        Parameters
        ----------
        data: dict
            The data dictionary.

        Returns
        -------
        layer
            The constructed vertical layer.
        """
        paths_data = data['paths']
        paths = [Path.from_data(paths_data[key]) for key in paths_data]
        layer = cls(id=None)
        layer.paths = paths
        layer.min_max_z_height = data['min_max_z_height']
        return layer


class VerticalLayersManager:
    """
    Creates empty vertical layers and assigns to the input paths to the fitting vertical layer using the add() function.
    The criterion for grouping paths to VerticalLayers is based on the proximity of the centroids of the paths.
    If the input paths don't fit in any vertical layer, then new vertical layer is created with that path.

    Attributes
    ----------
    max_paths_per_layer: int
        Maximum number of layers that a vertical layer can consist of.
        If None, then the vertical layer has an unlimited number of layers.
    """

    def __init__(self, avg_layer_height, max_paths_per_layer=None):
        self.layers = [VerticalLayer(id=0)]  # vertical_layers_print_data that contain isocurves (compas_slicer.Path)
        self.avg_layer_height = avg_layer_height
        self.max_paths_per_layer = max_paths_per_layer

    def add(self, path):
        selected_layer = None

        #  Find an eligible layer for path (called selected_layer)
        if len(self.layers[0].paths) == 0:  # first path goes to first layer
            selected_layer = self.layers[0]

        else:  # find the candidate segment for new isocurve
            centroid = np.mean(np.array(path.points), axis=0)
            other_centroids = get_vertical_layers_centroids_list(self.layers)
            candidate_layer = self.layers[utils.get_closest_pt_index(centroid, other_centroids)]

            threshold_max_centroid_dist = 5 * self.avg_layer_height
            if np.linalg.norm(candidate_layer.head_centroid - centroid) < threshold_max_centroid_dist:
                if self.max_paths_per_layer:
                    if len(candidate_layer.paths) < self.max_paths_per_layer:
                        selected_layer = candidate_layer
                else:
                    selected_layer = candidate_layer

                if selected_layer:  # also check that the actual distance between the layers is acceptable
                    pts_selected_layer = np.array(candidate_layer.paths[-1].points)
                    pts = np.array(path.points)
                    # find min distance between pts_selected_layer and pts
                    min_dist = 1e10  # some large number
                    max_dist = 0.0  # some small number
                    for pt in pts:
                        pt_array = np.tile(pt, (pts_selected_layer.shape[0], 1))
                        dists = np.linalg.norm(pts_selected_layer - pt_array, axis=1)
                        min_dist = min(np.min(dists), min_dist)
                        max_dist = max(np.min(dists), max_dist)
                    if min_dist > 3.0 * self.avg_layer_height or max_dist > 8.0 * self.avg_layer_height:
                        selected_layer = None

            if not selected_layer:  # then create new layer
                selected_layer = VerticalLayer(id=self.layers[-1].id + 1)
                self.layers.append(selected_layer)

        selected_layer.append_(path)


def get_vertical_layers_centroids_list(vert_layers):
    """ Returns a list with points that are the centroids of the heads of all vertical_layers_print_data. The head
    of a vertical_layer is its last path. """
    head_centroids = []
    for vert_layer in vert_layers:
        head_centroids.append(vert_layer.head_centroid)
    return head_centroids


if __name__ == "__main__":
    pass
