import compas
from compas.datastructures import Mesh
from compas_slicer.utilities import utils
from compas.geometry import Polyline

import logging

logger = logging.getLogger('logger')

__all__ = ['BaseSlicer']


class BaseSlicer(object):
    """
    Slicer class is an organizational class that holds all the information for the slice process
    This class is meant to be extended for the implementation of the various slicers.
    See PlanarSlicer as an example
    
    Attributes
    ----------
    mesh : compas.datastructures.Mesh 
        Input mesh
    """

    def __init__(self, mesh):
        ## check input
        assert isinstance(mesh, compas.datastructures.Mesh), \
            "Input mesh must be of type <compas.datastructures.Mesh>, not " + str(type(mesh))
        utils.check_triangular_mesh(mesh)

        ### input
        self.mesh = mesh
        logger.info(
            "Input Mesh with : %d vertices, %d Faces" % (len(list(self.mesh.vertices())), len(list(self.mesh.faces()))))

        self.layer_height = None

        self.path_collections = []  # any class inheriting from SortedPathCollection, i.e.  Layer(horizontal sorting)
        # or Segment (vertical sorting)

    ##############################
    ### --- Functions

    def slice_model(self, *args, **kwargs):
        raise NotImplementedError

    ##############################
    ### --- Output 

    def printout_info(self):
        open_paths = 0
        closed_paths = 0
        total_number_of_pts = 0
        number_of_path_collections = 0

        for path_collection in self.path_collections:
            number_of_path_collections += 1
            for path in path_collection.paths:
                total_number_of_pts += len(path.points)
                if path.is_closed:
                    closed_paths += 1
                else:
                    open_paths += 1

        print("\n---- Slicer Info ----")
        print("Number of path_collections: %d" % number_of_path_collections)
        print("Number of paths: %d, open paths: %d, closed paths: %d" % (
            open_paths + closed_paths, open_paths, closed_paths))
        print("Number of sampling printpoints on contours: %d" % total_number_of_pts)
        print("")

    def get_path_lines_for_plotter(self, color=(255, 0, 0)):
        lines = []
        for path_collection in self.path_collections:
            for path in path_collection.paths:
                lines.extend(path.get_lines_for_plotter(color))
        return lines

    def visualize_on_viewer(self, viewer, visualize_mesh, visualize_paths):
        if visualize_mesh:
            viewer.add(self.mesh, settings={'color': '#ff0000',
                                            'opacity': 0.4,})

        if visualize_paths:
            for i, path_collection in enumerate(self.path_collections):
                for j, path in enumerate(path_collection.paths):
                    polyline = Polyline(path.points)
                    viewer.add(polyline, name="Path_Collection %d, Path %d" % (i, j),
                               settings={'color': '#ffffff'})

        # for polyline in polylines:
        #     viewer.add(polyline, settings={'color': '#ffffff'})

    ##############################
    ### --- To json

    def to_json(self, filepath, name):
        utils.save_to_json(self.get_slicer_all_data_dict(), filepath, name)

    def flattened_paths_to_json(self, filepath, name):
        utils.save_to_json(self.get_flattened_path_dict(), filepath, name)

    def path_collections_to_json(self, filepath, name):
        utils.save_to_json(self.get_paths_collection_dict(), filepath, name)

    def get_slicer_all_data_dict(self):
        data = {'flattened_path': self.get_flattened_path_dict()}
        return data

    def get_flattened_path_dict(self):
        data = {}
        count = 0
        for path_collection in self.path_collections:
            for path in path_collection.paths:
                for point in path.points:
                    xyz = [point[0], point[1], point[2]]
                    data[count] = xyz
                    count += 1
        return data

    def get_paths_collection_dict(self):
        data = {}
        for i, path_collection in enumerate(self.path_collections):
            data[i] = {}
            for j, path in enumerate(path_collection.paths):
                data[i][j] = {}
                for k, point in enumerate(path.points):
                    data[i][j][k] = [point[0], point[1], point[2]]
        return data

if __name__ == "__main__":
    pass
