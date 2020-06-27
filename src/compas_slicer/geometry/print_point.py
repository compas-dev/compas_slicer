from compas.geometry import Point, Frame, distance_point_point_sqrd

__all__ = ['PrintPoint',
           'AdvancedPrintPoint']


class PrintPoint(object):
    def __init__(self, pt, layer_height):
        self.pt = pt  # position of center of mass (compas.geometry.Point)
        self.layer_height = layer_height

        self.parent_path = None  # class inheriting from PrintPath. The path in which this point belongs

    #### --- Find neighboring points
    def get_prev_print_point(self):
        assert self.parent_path, "Cannot get neighboring points because parent_path has not been specified"
        i = self.parent_path.points.index(self)
        if i > 0:
            return self.parent_path.points[i - 1]

    def get_next_print_point(self):
        assert self.parent_path, "Cannot get neighboring points because parent_path has not been specified"
        i = self.parent_path.points.index(self)
        if i < len(self.parent_path.points) - 1:
            return self.parent_path.points[i + 1]


class AdvancedPrintPoint(PrintPoint):
    def __init__(self, pt, layer_height, up_vector, mesh):
        PrintPoint.__init__(self, pt, layer_height)
        self.pt = pt  # position of center of mass (compas.geometry.Point)
        self.layer_height = layer_height
        self.up_vector = up_vector  # compas.geometry.Vector

        self.normal = self.get_closest_mesh_normal(mesh)  # compas.geometry.Vector
        self.frame = self.get_frame()  # compas.geometry.Frame

        ### ----- parameters currently not yet filled in
        self.visualization_shape = None
        # parameters useful for curved slicing
        self.support_printpoint = None  # class PrintPoint
        self.support_path = None  # class inheriting from PrintPath

    #### --- Initialization functions
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
