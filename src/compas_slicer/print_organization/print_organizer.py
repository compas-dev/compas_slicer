import compas_slicer
import logging
from compas_slicer.geometry import PrintPoint
from compas.geometry import Polyline
import compas_slicer.utilities as utils
import progressbar
import numpy as np
from compas_slicer.print_organization import get_blend_radius

logger = logging.getLogger('logger')

__all__ = ['PrintOrganizer']


class PrintOrganizer(object):
    """
    Base class for organizing the printing process.

    slicer: compas_slicer.slicers.BaseSlicer
    """

    def __init__(self, slicer):
        assert isinstance(slicer, compas_slicer.slicers.BaseSlicer)  # check input
        logger.info('Print Organizer')
        self.slicer = slicer
        self.printpoints_dict = {}

    def __repr__(self):
        return "<PrintOrganizer>"

    ###############################
    #  --- Initialization
    def create_printpoints(self, mesh):
        logger.info('Creating print points ...')
        with progressbar.ProgressBar(max_value=len(self.slicer.layers)) as bar:

            for i, layer in enumerate(self.slicer.layers):
                self.printpoints_dict['layer_%d' % i] = {}

                for j, path in enumerate(layer.paths):
                    self.printpoints_dict['layer_%d' % i]['path_%d' % j] = []

                    for k, point in enumerate(path.points):
                        normal = utils.get_normal_of_path_on_xy_plane(k, point, path, mesh)

                        printpoint = PrintPoint(pt=point, layer_height=self.slicer.layer_height,
                                                mesh_normal=normal)

                        self.printpoints_dict['layer_%d' % i]['path_%d' % j].append(printpoint)
                bar.update()

    @property
    def number_of_layers(self):
        return len(self.printpoints_dict)

    def number_of_paths_on_layer(self, layer_index):
        return len(self.printpoints_dict['layer_%d' % layer_index])

    ###############################
    #  ---  TODO

    def check_feasibility(self):
        """General description.
        """
        # TODO
        raise NotImplementedError

    ###############################
    #  ---  output printpoints data
    def output_printpoints_dict(self):
        data = {}

        count = 0
        for layer_key in self.printpoints_dict:
            for path_key in self.printpoints_dict[layer_key]:
                self.remove_duplicate_points_in_path(layer_key, path_key)

                for i, printpoint in enumerate(self.printpoints_dict[layer_key][path_key]):
                    neighboring_items = self.get_printpoint_neighboring_items(layer_key, path_key, i)
                    printpoint.blend_radius = get_blend_radius(printpoint, neighboring_items)

                    data[count] = printpoint.to_data()

                    count += 1
        logger.info("Generated %d print points" % count)
        return data

    def remove_duplicate_points_in_path(self, layer_key, path_key):
        """Remove subsequent points that are within a certain tolerance."""
        dup_index = []
        # find duplicates
        duplicate_ppts = []
        for i, printpoint in enumerate(self.printpoints_dict[layer_key][path_key]):
            if i < len(self.printpoints_dict[layer_key][path_key]) - 1:
                next = self.printpoints_dict[layer_key][path_key][i + 1]
                if np.linalg.norm(np.array(printpoint.pt) - np.array(next.pt)) < 0.0001:
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

    def get_printpoint_neighboring_items(self, layer_key, path_key, i):
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

    ##################################
    #  --- Visualization on viewer
    def visualize_on_viewer(self, viewer, visualize_polyline, visualize_printpoints):
        """Visualize printpoints on the viewer."""
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


if __name__ == "__main__":
    pass
