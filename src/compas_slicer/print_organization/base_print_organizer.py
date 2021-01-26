import compas_slicer
import logging
from compas.geometry import Polyline, distance_point_point
import numpy as np
from abc import abstractmethod

logger = logging.getLogger('logger')

__all__ = ['BasePrintOrganizer']


class BasePrintOrganizer(object):
    """
    Base class for organizing the printing process.
    This class is meant to be extended for the implementation of the various print organizers.
    Do not use this class directly in your python code. Instead use PlanarPrintOrganizer or CurvedPrintOrganizer.

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
    def create_printpoints(self, transfer_attributes=False):
        """To be implemented by the inheriting classes"""
        pass

    @abstractmethod
    def check_printpoints_feasibility(self):
        """To be implemented by the inheriting classes"""
        pass

    ######################
    # Properties
    ######################

    @property
    def total_number_of_points(self):
        """int: Total number of points in the PrintOrganizer."""
        total_number_of_pts = 0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for printpoint in self.printpoints_dict[layer_key][path_key]:
                    total_number_of_pts += 1
        return total_number_of_pts

    @property
    def number_of_layers(self):
        """int: Number of layers in the PrintOrganizer."""
        return len(self.printpoints_dict)

    def number_of_paths_on_layer(self, layer_index):
        """int: Number of paths within a Layer of the PrintOrganizer."""
        return len(self.printpoints_dict['layer_%d' % layer_index])

    ######################
    # Utils
    ######################

    def remove_duplicate_points_in_path(self, layer_key, path_key, tolerance=0.0001):
        """Remove subsequent points that are within a certain tolerance.

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
                'Attention! %d Duplicate printpoint(s) ' % len(duplicate_ppts)
                + 'on ' + layer_key + ', ' + path_key + ', indices: ' + str(dup_index) + '. They will be removed.')

        # remove duplicates
        if len(duplicate_ppts) > 0:
            for ppt in duplicate_ppts:
                self.printpoints_dict[layer_key][path_key].remove(ppt)

    def transfer_attributes_to_point(self, point):
        # project point on mesh


        attributes = {}
        return attributes

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

        layers = 0
        paths = 0
        total_number_of_pts = 0
        total_time = 0
        total_length = 0
        flat_dict = []

        for layer_key in self.printpoints_dict:
            layers += 1
            for path_key in self.printpoints_dict[layer_key]:
                paths += 1
                for printpoint in self.printpoints_dict[layer_key][path_key]:
                    flat_dict.append(printpoint)
                    total_number_of_pts += 1

        for i in range(len(flat_dict)):
            curr = flat_dict[i]
            prev = flat_dict[i - 1]

            if i > 0:
                # calculate length of toolpath
                length = distance_point_point(prev.pt, curr.pt)
                total_length += length
                # get speed for every section and calculate time
                if curr.velocity:
                    speed = curr.velocity
                    time = length / speed
                    total_time += time

        min, sec = divmod(total_time, 60)
        hour, min = divmod(min, 60)

        print("\n---- PrintOrganizer Info ----")
        print("Number of layers: %d" % layers)
        print("Number of paths: %d" % paths)
        print("Number of PrintPoints: %d" % total_number_of_pts)
        print("Toolpath length: %d mm" % total_length)
        print("Printing time: %d hours, %02d min, %02d sec" % (hour, min, sec))
        print("")

    def visualize_on_viewer(self, viewer, visualize_polyline, visualize_printpoints):
        """Visualize printpoints on the compas_viewer.

        Parameters
        ----------
        viewer: :class: 'compas_viewers.objectviewer.ObjectViewer'
        visualize_polyline: bool
        visualize_printpoints: bool
        """
        all_pts = []
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                for printpoint in self.printpoints_dict[layer_key][path_key]:
                    all_pts.append(printpoint.pt)

        if visualize_polyline:
            polyline = Polyline(all_pts)
            viewer.add(polyline, name="Polyline", settings={'color': '#ffffff'})

        if visualize_printpoints:
            [viewer.add(pt, name="Point %d" % i) for i, pt in enumerate(all_pts)]

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
        gcode = compas_slicer.print_organization.create_gcode_text(self.printpoints_dict, parameters)
        return gcode


if __name__ == "__main__":
    pass
