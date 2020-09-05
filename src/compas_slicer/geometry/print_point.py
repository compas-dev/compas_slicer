from compas.geometry import Point, Frame, distance_point_point_sqrd

__all__ = ['PrintPoint']


class PrintPoint(object):
    def __init__(self, pt, layer_height):

        ### --- basic printpoint
        self.pt = pt  # position of center of mass (compas.geometry.Point)

        self.layer_height = layer_height  # float
        self.parent_path = None  # class inheriting from Path. The path in which this point belongs

        self.extruder_toggle = None  # boolean

        ### --- advanced printpoint
        self.up_vector = None  # compas.geometry.Vector
        self.normal = None  # compas.geometry.Vector
        self.frame = None  # compas.geometry.Frame

        self.support_path = None  # class inheriting from Path. The path that is directly under the printpoint
        self.support_printpoint = None  # class PrintPoint

        self.visualization_geometry = None

    #### --- Find neighboring printpoints
    def get_prev_print_point(self):
        assert self.parent_path, "Cannot get neighboring printpoints because parent_path has not been specified"
        i = self.parent_path.printpoints.index(self)
        if i > 0:
            return self.parent_path.printpoints[i - 1]

    def get_next_print_point(self):
        assert self.parent_path, "Cannot get neighboring printpoints because parent_path has not been specified"
        i = self.parent_path.printpoints.index(self)
        if i < len(self.parent_path.printpoints) - 1:
            return self.parent_path.printpoints[i + 1]

    #### --- Initialization of advanced print point functions

    def initialize_advanced_print_point(self, mesh, up_vector):
        self.up_vector = up_vector
        self.normal = self.get_closest_mesh_normal(mesh)
        self.frame = self.get_frame()

    def get_frame(self):
        return Frame(self.pt, self.up_vector, self.normal)

    def get_closest_mesh_normal(self, mesh):
        vertex_tupples = [(v_key, Point(data['x'], data['y'], data['z'])) for v_key, data in mesh.vertices(data=True)]
        # sort according to distance from self.pt
        vertex_tupples = sorted(vertex_tupples, key=lambda v_tupple: distance_point_point_sqrd(self.pt, v_tupple[1]))
        closest_vkey = vertex_tupples[0][0]
        return mesh.vertex_normal(closest_vkey)

    #### --- Visualization
    def generate_visualization_shape(self):
        pass  # TODO
