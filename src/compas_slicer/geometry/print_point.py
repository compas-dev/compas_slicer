from compas.geometry import Point, Frame, distance_point_point_sqrd, Vector

__all__ = ['PrintPoint']


def get_default_print_frame(pt, desired_axis):
    desired_second_axis = Vector(1, 0, 0)
    return Frame(pt, desired_axis, desired_second_axis)


class PrintPoint(object):
    """
    A PrintPoint consists out of a single compas.geometry.Point, 
    with additional functionality added for the printing process.

    Attributes
    ----------
    pt : compas.geometry.Point
        A compas Point consisting out of x, y, z coordinates
    layer_height : float
        The vertical distance between the point on this layer and the next layer
    """

    def __init__(self, pt, layer_height):
        ### --- basic printpoint
        self.pt = pt
        self.layer_height = layer_height
        self.extruder_toggle = None
        self.velocity = None

        self.wait_time = 0
        self.print_frame = get_default_print_frame(pt, desired_axis=Vector(0, 1, 0))  # compas.geometry.Frame

        ### --- advanced printpoint
        self.up_vector = None  # compas.geometry.Vector
        self.mesh_normal = None  # compas.geometry.Vector
        self.plane = None

        self.closest_support_pt = None  # class compas.geometry.point
        self.closest_upper_point = None
        self.distance_to_support = None

        self.visualization_geometry = None

    def __repr__(self):
        x, y, z = self.pt[0], self.pt[1], self.pt[2]
        return "<PrintPoint object at (%.2f, %.2f, %.2f)>" % (x, y, z)

    #### --- Initialization of advanced print point functions

    def initialize_advanced_print_point(self, mesh, up_vector):
        self.up_vector = up_vector
        self.normal = self.get_closest_mesh_normal(mesh)
        self.plane = self.get_plane()
        # update print frame with correct plane orientation
        self.print_frame = get_default_print_frame(pt=self.pt, desired_axis=self.plane.xaxis.scaled(-1))

    def get_plane(self):
        return Frame(self.pt, self.up_vector, self.mesh_normal)

    def get_closest_mesh_normal(self, mesh):
        vertex_tupples = [(v_key, Point(data['x'], data['y'], data['z'])) for v_key, data in mesh.vertices(data=True)]
        # sort according to distance from self.pt
        vertex_tupples = sorted(vertex_tupples, key=lambda v_tupple: distance_point_point_sqrd(self.pt, v_tupple[1]))
        closest_vkey = vertex_tupples[0][0]
        return mesh.vertex_normal(closest_vkey)

    #################################
    #### --- Visualization
    def generate_visualization_shape(self):
        raise NotImplementedError  # TODO

    #################################
    #### --- To data , from data
    def to_data(self):
        if self.closest_upper_point:
            closest_upper_point = [self.closest_upper_point[0], self.closest_upper_point[1],
                                   self.closest_upper_point[2]]
        else:
            closest_upper_point = None

        if self.closest_support_pt:
            closest_support_pt = [self.closest_support_pt[0], self.closest_support_pt[1], self.closest_support_pt[2]]
        else:
            closest_support_pt = None

        point = {
            "point": [self.pt[0], self.pt[1], self.pt[2]],
            "closest_support_pt": closest_support_pt,
            "distance_to_support": self.distance_to_support,
            "closest_upper_point": closest_upper_point,
            "up_vector": [self.up_vector[0], self.up_vector[1], self.up_vector[2]],
            "layer_height": self.layer_height,
            "frame": {'point': [self.frame.point[0], self.frame.point[1], self.frame.point[2]],
                      'xaxis': [self.frame.xaxis[0], self.frame.xaxis[1], self.frame.xaxis[2]],
                      'yaxis': [self.frame.yaxis[0], self.frame.yaxis[1], self.frame.yaxis[2]]},
            "mesh_normal": [self.mesh_normal[0], self.mesh_normal[1], self.mesh_normal[2]]
        }
        return point

    @classmethod
    def from_data(cls, data):
        pp = cls(pt=Point(data['point'][0], data['point'][1], data['point'][2]),
                 layer_height=data['layer_height'])

        if data['closest_support_pt']:
            pp.closest_support_pt = Point(data['closest_support_pt'][0],
                                          data['closest_support_pt'][1],
                                          data['closest_support_pt'][2])

        if data['distance_to_support']:
            pp.distance_to_support = data['distance_to_support']

        if data['closest_upper_point']:
            pp.closest_upper_point = Point(data['closest_upper_point'][0],
                                           data['closest_upper_point'][1],
                                           data['closest_upper_point'][2])

        if data['up_vector']:
            pp.up_vector = Vector(data['up_vector'][0], data['up_vector'][1], data['up_vector'][2])

        if data['frame']:
            pp.frame = Frame(
                Point(data['frame']['point'][0], data['frame']['point'][1], data['frame']['point'][2]),
                Vector(data["frame"]["xaxis"][0], data['frame']['xaxis'][1],
                       data['frame']['xaxis'][2]),
                Vector(data['frame']['yaxis'][0], data['frame']['yaxis'][1],
                       data['frame']['yaxis'][2]))

        if data['mesh_normal']:
            pp.mesh_normal = Vector(data['mesh_normal'][0], data['mesh_normal'][1], data['mesh_normal'][2])

        return pp
