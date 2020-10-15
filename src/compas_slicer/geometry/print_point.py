from compas.geometry import Point, Frame, distance_point_point_sqrd, Vector
import compas
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
    mesh:
    up_vector:

    """

    def __init__(self, pt, layer_height, mesh_normal, up_vector):
        #  --- basic printpoint
        self.pt = pt
        self.layer_height = layer_height

        assert isinstance(mesh_normal, compas.geometry.Vector)

        self.up_vector = up_vector  # compas.geometry.Vector
        self.mesh_normal = mesh_normal  # compas.geometry.Vector
        self.frame = self.get_frame()  # compas.geometry.Frame

        #  --- print_organization related attributes
        self.extruder_toggle = None
        self.velocity = None
        self.wait_time = None

        #  --- advanced printpoint
        self.closest_support_pt = None  # class compas.geometry.point
        self.closest_upper_point = None
        self.distance_to_support = None

        self.visualization_geometry = None

    def __repr__(self):
        x, y, z = self.pt[0], self.pt[1], self.pt[2]
        return "<PrintPoint object at (%.2f, %.2f, %.2f)>" % (x, y, z)

    def get_frame(self):
        return Frame(self.pt, self.up_vector, self.mesh_normal)

    #################################
    #  --- To data , from data
    def to_data(self):
        point = {
            "point": [self.pt[0], self.pt[1], self.pt[2]],
            "up_vector": self.up_vector.to_data(),
            "layer_height": self.layer_height,
            "frame": self.frame.to_data(),
            "mesh_normal": self.mesh_normal.to_data(),

            "closest_support_pt": self.closest_support_pt.to_data() if self.closest_support_pt else None,
            "distance_to_support": self.distance_to_support.to_data() if self.distance_to_support else None,
            "closest_upper_point": self.closest_upper_point.to_data() if self.closest_upper_point else None,
        }
        return point

    @classmethod
    def from_data(cls, data):
        pp = cls(pt=Point(data['point'][0], data['point'][1], data['point'][2]),
                 layer_height=data['layer_height'], mesh_normal=data['mesh_normal'].from_data(),
                 up_vector=Vector.from_data(data['up_vector']))

        pp.frame = Frame.from_data(data['frame'])

        pp.closest_support_pt = Point.from_data(data['closest_support_pt'])
        pp.distance_to_support = data['distance_to_support']
        pp.closest_upper_point = Point.from_data(data['closest_upper_point'])

        return pp
