import compas
import compas_slicer
from compas.datastructures import Mesh
from compas_slicer.utilities import utils
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
        self.check_triangular_mesh(mesh)

        ### input
        self.mesh = mesh
        logger.info("Input Mesh with : %d vertices, %d Faces" % (len(list(self.mesh.vertices())), len(list(self.mesh.faces()))))

        self.print_paths = []  # any class inheriting from SortedPathCollection, i.e.  Layer(horizontal sorting) or Segment (vertical sorting)

    def slice_model(self, *args, **kwargs):
        raise NotImplementedError

    ##############################
    ### --- Output 

    def printout_info(self):
        open_contours = 0
        closed_contours = 0
        total_number_of_pts = 0
        number_of_print_paths = 0

        for layer in self.print_paths:
            number_of_print_paths += 1
            for contour in layer.contours:
                total_number_of_pts += len(contour.printpoints)
                if contour.is_closed:
                    closed_contours += 1
                else:
                    open_contours += 1

        print("\n---- Slicer Info ----")
        print("Number of print_paths: %d" % number_of_print_paths)
        print("Number of contours: %d, open contours: %d, closed contours: %d" % (
            open_contours + closed_contours, open_contours, closed_contours))
        print("Number of sampling printpoints on contours: %d" % total_number_of_pts)
        print("")

    def get_contour_lines_for_plotter(self, color=(255, 0, 0)):
        lines = []
        for layer in self.print_paths:
            for contour in layer.contours:
                lines.extend(contour.get_lines_for_plotter(color))
        return lines

    ##############################
    ### --- For visualization
    def to_json(self, path, name):
        data = {}

        contours = self.contours_to_json(path, name)
        data['contours'] = contours

        utils.save_to_json(data, path, name)


    def contours_to_json(self, path, name):
        data = {}
        count = 0
        for collection in self.print_paths:
            for contour in collection.contours:
                for printpoint in contour.printpoints:
                    xyz = [printpoint[0], printpoint[1], printpoint[2]]
                    data[count] = xyz
                    count += 1
        return data

    def layers_to_json(self, path, name):
        data = {}
        count = 0
        d = []
        for layers in self.print_paths:
            l = []
            for contour in layers.contours:
                pts_per_contour = []
                for printpoint in contour.printpoints:
                    xyz = [printpoint[0], printpoint[1], printpoint[2]]
                    pts_per_contour.append(xyz)
                l.append(pts_per_contour)
            d.append(l)    
        
        data = d
        
        utils.save_to_json(data, path, name)

    ##############################
    ### --- Other 

    def check_triangular_mesh(self, mesh):
        for fkey in mesh.faces():
            vs = mesh.face_vertices(fkey)
            if len(vs) != 3:
                raise TypeError("Found a quad at face key: " + str(fkey) + " ,number of face vertices:" + str(
                    len(vs)) + ". \nOnly triangular meshes supported.")

    def generate_z_hop(self, z_hop):
        logger.info("Generating z_hop of XX mm")
        compas_slicer.slicers.generate_z_hop(self.print_paths, z_hop)


if __name__ == "__main__":
    pass
