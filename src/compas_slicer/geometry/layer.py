import logging
import compas_slicer
import numpy as np
from compas_slicer.geometry import Path

logger = logging.getLogger('logger')

__all__ = ['Layer',
           'VerticalLayer']


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
    z_height: float
        Z height of the layer.
    """

    def __init__(self, paths):
        # check input
        if paths is None:
            paths = []
        if len(paths) > 0:
            assert isinstance(paths[0], compas_slicer.geometry.Path)
        self.paths = paths

        # brim
        self.is_brim = False
        self.number_of_brim_offsets = None

        # gets z height of layer by checking first point
        if paths:
            self.z_height = paths[0].points[0][2]

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
        return layer

    def to_data(self):
        """Returns a dictionary of structured data representing the data structure.

        Returns
        -------
        dict
            The layers's data.

        """
        data = {'paths': {i: [] for i in range(len(self.paths))},
                'layer_type': 'horizontal_layer',
                'is_brim': self.is_brim,
                'number_of_brim_offsets': self.number_of_brim_offsets}
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
    min_max_z_height: tuple
        Tuple containing the minimum and maximum z height of the VerticalLayer.
    """

    def __init__(self, id=0, paths=None):
        Layer.__init__(self, paths=paths)
        self.id = id
        self.head_centroid = None
        self.min_max_z_height = None

    def __repr__(self):
        no_of_paths = len(self.paths) if self.paths else 0
        return "<Vertical Layer object with id : %d and %d paths>" % (self.id, no_of_paths)

    def append_(self, path):
        """ Add path to self.paths list. """
        self.paths.append(path)
        self.compute_head_centroid()

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
            The vertical layers's data.

        """
        data = {'paths': {i: [] for i in range(len(self.paths))},
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
        return layer


if __name__ == "__main__":
    pass
