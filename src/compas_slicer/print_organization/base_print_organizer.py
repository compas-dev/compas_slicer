import compas_slicer
import logging
from compas.geometry import Vector, distance_point_point, norm_vector, normalize_vector, subtract_vectors, \
    cross_vectors, scale_vector
from compas.utilities import pairwise
import numpy as np
from abc import abstractmethod

logger = logging.getLogger('logger')

__all__ = ['BasePrintOrganizer']


class BasePrintOrganizer(object):
    """
    Base class for organizing the printing process.
    This class is meant to be extended for the implementation of the various print organizers.
    Do not use this class directly in your python code. Instead use PlanarPrintOrganizer or InterpolationPrintOrganizer.

    Attributes
    ----------
    slicer: :class:`compas_slicer.slicers.PlanarSlicer`
        An instance of the compas_slicer.slicers.PlanarSlicer.
    """

    def __init__(self, slicer):
        assert isinstance(slicer, compas_slicer.slicers.BaseSlicer)  # check input
        logger.info('Print Organizer')
        self.slicer = slicer
        self.printpoints_dict = {}

    def __repr__(self):
        return "<BasePrintOrganizer>"

    ######################
    # Abstract methods
    ######################

    @abstractmethod
    def create_printpoints(self):
        """To be implemented by the inheriting classes"""
        pass

    ######################
    # Iterators
    ######################
    def printpoints_iterator(self):
        """
        Iterate over the printpoints of the print organizer.

        Yields
        ------
        printpoint: :class: 'compas_slicer.geometry.Printpoint'
        """
        assert len(self.printpoints_dict) > 0, 'No printpoints have been created.'
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for printpoint in self.printpoints_dict[layer_key][path_key]:
                    yield printpoint

    def printpoints_indices_iterator(self):
        """
        Iterate over the printpoints of the print organizer.

        Yields
        ------
        printpoint: :class: 'compas_slicer.geometry.Printpoint'
        i: int, layer index. To get the layer key use: layer_key = 'layer_%d' % i
        j: int, path index. To get the path key use: path_key = 'path_%d' % j
        k: int, printpoint index
        """
        assert len(self.printpoints_dict) > 0, 'No printpoints have been created.'
        for i, layer_key in enumerate(self.printpoints_dict):
            for j, path_key in enumerate(self.printpoints_dict[layer_key]):
                for k, printpoint in enumerate(self.printpoints_dict[layer_key][path_key]):
                    yield printpoint, i, j, k

    ######################
    # Properties
    ######################

    @property
    def number_of_printpoints(self):
        """int: Total number of points in the PrintOrganizer."""
        total_number_of_pts = 0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for _ in self.printpoints_dict[layer_key][path_key]:
                    total_number_of_pts += 1
        return total_number_of_pts

    @property
    def number_of_paths(self):
        total_number_of_paths = 0
        for layer_key in self.printpoints_dict:
            for _ in self.printpoints_dict[layer_key]:
                total_number_of_paths += 1
        return total_number_of_paths

    @property
    def number_of_layers(self):
        """int: Number of layers in the PrintOrganizer."""
        return len(self.printpoints_dict)

    @property
    def total_length_of_paths(self):
        """ Returns the total length of all paths. Does not consider extruder toggle. """
        total_length = 0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for prev, curr in pairwise(self.printpoints_dict[layer_key][path_key]):
                    length = distance_point_point(prev.pt, curr.pt)
                    total_length += length
        return total_length

    @property
    def total_print_time(self):
        """ If the print speed is defined, it returns the total time of the print, else returns None"""
        if self.printpoints_dict['layer_0']['path_0'][0].velocity is not None:  # assume that all ppts are set or none
            total_time = 0
            for layer_key in self.printpoints_dict:
                for path_key in self.printpoints_dict[layer_key]:
                    for prev, curr in pairwise(self.printpoints_dict[layer_key][path_key]):
                        length = distance_point_point(prev.pt, curr.pt)
                        total_time += length / curr.velocity
            return total_time

    def number_of_paths_on_layer(self, layer_index):
        """int: Number of paths within a Layer of the PrintOrganizer."""
        return len(self.printpoints_dict['layer_%d' % layer_index])

    ######################
    # Utils
    ######################

    def remove_duplicate_points_in_path(self, layer_key, path_key, tolerance=0.0001):
        """Remove subsequent points that are within a certain threshold.

        Parameters
        ----------
        layer_key: str
            They key of the layer to remove points from.
        path_key: str
            The key of the path to remove points from.
        tolerance: float, optional
            Distance between points to remove. Defaults to 0.0001.
        """

        dup_index = []
        # find duplicates
        duplicate_ppts = []
        for i, printpoint in enumerate(self.printpoints_dict[layer_key][path_key]):
            if i < len(self.printpoints_dict[layer_key][path_key]) - 1:
                next_ppt = self.printpoints_dict[layer_key][path_key][i + 1]
                if np.linalg.norm(np.array(printpoint.pt) - np.array(next_ppt.pt)) < tolerance:
                    dup_index.append(i)
                    duplicate_ppts.append(printpoint)

        # warn user
        if len(duplicate_ppts) > 0:
            logger.warning(
                'Attention! %d Duplicate printpoint(s) ' % len(duplicate_ppts) + 'on ' + layer_key + ', ' + path_key +
                ', indices: ' + str(dup_index) + '. They will be removed.')

        # remove duplicates
        if len(duplicate_ppts) > 0:
            for ppt in duplicate_ppts:
                self.printpoints_dict[layer_key][path_key].remove(ppt)

    def get_printpoint_neighboring_items(self, layer_key, path_key, i):
        """
        layer_key: str
            They key of the layer the current printpoint belongs to.
        path_key: str
            They key of the path the current printpoint belongs to.
        i: int
            The index of the current printpoint.

        Returns
        ----------
        list, :class:  'compas_slicer.geometry.PrintPoint'
        """
        neighboring_items = []
        if i > 0:
            neighboring_items.append(self.printpoints_dict[layer_key][path_key][i - 1])
        else:
            neighboring_items.append(None)
        if i < len(self.printpoints_dict[layer_key][path_key]) - 1:
            neighboring_items.append(self.printpoints_dict[layer_key][path_key][i + 1])
        else:
            neighboring_items.append(None)
        return neighboring_items

    def printout_info(self):
        """Prints out information from the PrintOrganizer"""
        ppts_attributes = {}
        for key in self.printpoints_dict['layer_0']['path_0'][0].attributes:
            ppts_attributes[key] = str(type(self.printpoints_dict['layer_0']['path_0'][0].attributes[key]))

        print("\n---- PrintOrganizer Info ----")
        print("Number of layers: %d" % self.number_of_layers)
        print("Number of paths: %d" % self.number_of_paths)
        print("Number of PrintPoints: %d" % self.number_of_printpoints)
        print("PrintPoints attributes: ")
        for key in ppts_attributes:
            print('     % s : % s' % (str(key), ppts_attributes[key]))
        print("Toolpath length: %d mm" % self.total_length_of_paths)

        print_time = self.total_print_time
        if print_time:
            minutes, sec = divmod(self.total_print_time, 60)
            hour, minutes = divmod(minutes, 60)
            print("Total print time: %d hours, %d minutes, %d seconds" % (hour, minutes, sec))
        else:
            print("Print Velocity has not been assigned, thus print time is not calculated.")
        print("")

    def get_printpoint_up_vector(self, path, k, normal):
        """
        Returns the printpoint up-vector so that it is orthogonal to the path direction and the normal

        Parameters
        ----------
        path: :class:`compas_slicer.geometry.Path`
        k: the index of the point in path.points that the PrintPoint represents
        normal: :class:`compas.geometry.Vector`
        """

        p = path.points[k]
        if k < len(path.points) - 1:
            negative = False
            other_pt = path.points[k + 1]
        else:
            negative = True
            other_pt = path.points[k - 1]
        diff = normalize_vector(subtract_vectors(p, other_pt))
        up_vec = normalize_vector(cross_vectors(normal, diff))
        if negative:
            up_vec = scale_vector(up_vec, -1.0)
        if norm_vector(up_vec) == 0:
            up_vec = Vector(0, 0, 1)
        return Vector(*up_vec)

    ######################
    # Output data
    ######################

    def output_printpoints_dict(self):
        """Creates a flattened PrintPoints as a dictionary.

        Returns
        ----------
        dict, with printpoints that can be saved as json
        """
        data = {}

        count = 0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                self.remove_duplicate_points_in_path(layer_key, path_key)
                for printpoint in self.printpoints_dict[layer_key][path_key]:
                    data[count] = printpoint.to_data()

                    count += 1
        logger.info("Generated %d print points" % count)
        return data

    def output_nested_printpoints_dict(self):
        """Creates a nested PrintPoints as a dictionary.

        Returns
        ----------
        dict, with printpoints that can be saved as json
        """
        data = {}

        count = 0
        for layer_key in self.printpoints_dict:
            data[layer_key] = {}
            for path_key in self.printpoints_dict[layer_key]:
                data[layer_key][path_key] = {}
                self.remove_duplicate_points_in_path(layer_key, path_key)
                for i, printpoint in enumerate(self.printpoints_dict[layer_key][path_key]):
                    data[layer_key][path_key][i] = printpoint.to_data()

                    count += 1

        logger.info("Generated %d print points" % count)
        return data

    def output_gcode(self, parameters):
        """ Gets a gcode text file using the function that creates gcode
        Parameters
        ----------
        parameters: dict with gcode parameters

        Returns
        ----------
        str, gcode text file
        """
        # check print organizer: Should have horizontal layers, ideally should be planar
        # ...
        gcode = compas_slicer.print_organization.create_gcode_text(self, parameters)
        return gcode

    def get_printpoints_attribute(self, attr_name):
        """
        Returns a list of printpoint attributes that have key=attr_name.

        Parameters
        ----------
        attr_name: str

        Returns
        -------
        list of size len(ppts) with whatever type the ppts.attribute[attr_name] is.
        """
        attr_values = []
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for ppt in self.printpoints_dict[layer_key][path_key]:
                    assert attr_name in ppt.attributes, \
                        "The attribute '%s' is not in the printpoint.attributes" % attr_name
                    attr_values.append(ppt.attributes[attr_name])
        return attr_values


if __name__ == "__main__":
    pass
