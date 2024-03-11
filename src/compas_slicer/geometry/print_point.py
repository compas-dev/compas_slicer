from compas.geometry import Point, Frame, Vector, cross_vectors, dot_vectors, norm_vector
import compas_slicer.utilities.utils as utils
import compas

__all__ = ['PrintPoint']


class PrintPoint(object):
    """
    A PrintPoint consists of a compas.geometry.Point,
    and additional attributes related to the printing process.

    Attributes
    ----------
    pt: :class:`compas.geometry.Point`
        A compas Point consisting out of x, y, z coordinates.
    layer_height: float
        The distance between the point on this layer and the previous layer.
        For planar slicing this is the vertical distance, for curved slicing this is absolute distance.
    mesh_normal: :class:`compas.geometry.Vector`
        Normal of the mesh at this PrintPoint.
    up_vector: :class:`compas.geometry.Vector`
        Vector in up direction. For planar slicing this corresponds to the z axis, for curved slicing it varies.
    frame: :class:`compas.geometry.Frame`
        Frame with x-axis pointing up, y-axis pointing towards the mesh normal.
    extruder_toggle: bool
        True if extruder should be on (when printing), False if it should be off (when travelling).
    velocity: float
        Velocity to use for printing (print speed), in mm/s.
    wait_time: float
        Time in seconds to wait at this PrintPoint.
    """

    def __init__(self, pt, layer_height, mesh_normal):
        assert isinstance(pt, compas.geometry.Point)
        assert isinstance(mesh_normal, compas.geometry.Vector)
        assert layer_height

        #  --- basic printpoint
        self.pt = pt
        self.layer_height = layer_height

        self.mesh_normal = mesh_normal  # compas.geometry.Vector
        self.up_vector = Vector(0, 0, 1)  # default value that can be updated
        self.frame = self.get_frame()  # compas.geometry.Frame

        #  --- attributes transferred from the mesh (vertex / face attributes)
        self.attributes = {}  # dict. To fill this in,

        #  --- print_organization related attributes
        self.extruder_toggle = None  # bool
        self.velocity = None  # float (mm/s)
        self.wait_time = None  # float (sec)
        self.blend_radius = None  # float (mm)

        #  --- relation to support
        self.closest_support_pt = None  # <compas.geometry.Point>
        self.distance_to_support = None  # float

        self.is_feasible = True  # bool

    def __repr__(self):
        x, y, z = self.pt[0], self.pt[1], self.pt[2]
        return "<PrintPoint object at (%.2f, %.2f, %.2f)>" % (x, y, z)

    def get_frame(self):
        """ Returns a Frame with x-axis pointing up, y-axis pointing towards the mesh normal. """
        if abs(dot_vectors(self.up_vector, self.mesh_normal)) < 1.0:  # if the normalized vectors are not co-linear
            c = cross_vectors(self.up_vector, self.mesh_normal)
            if norm_vector(c) == 0:
                c = Vector(1, 0, 0)
            if norm_vector(self.mesh_normal) == 0:
                self.mesh_normal = Vector(0, 1, 0)
            return Frame(self.pt, c, self.mesh_normal)
        else:  # in horizontal surfaces the vectors happen to be co-linear
            return Frame(self.pt, Vector(1, 0, 0), Vector(0, 1, 0))

    #################################
    #  --- To data , from data
    def to_data(self):
        """Returns a dictionary of structured data representing the data structure.
        TODO: The attributes of the printpoints are not saved in the dictionary because they can be non-Json
        serializable. Find a solution for this.

        Returns
        -------
        dict
            The PrintPoints' data.

        """
        point = {
            'point': [self.pt[0], self.pt[1], self.pt[2]],
            'layer_height': self.layer_height,

            'mesh_normal': self.mesh_normal.to_data(),
            'up_vector': self.up_vector.to_data(),
            'frame': self.frame.to_data(),

            'extruder_toggle': self.extruder_toggle,
            'velocity': self.velocity,
            'wait_time': self.wait_time,
            'blend_radius': self.blend_radius,

            'closest_support_pt': self.closest_support_pt.to_data() if self.closest_support_pt else None,
            'distance_to_support': self.distance_to_support,

            'is_feasible': self.is_feasible,

            'attributes': utils.get_jsonable_attributes(self.attributes)
        }
        return point

    @classmethod
    def from_data(cls, data):
        """Construct a PrintPoint from its data representation.

        Parameters
        ----------
        data: dict
            The data dictionary.

        Returns
        -------
        layer
            The constructed PrintPoint.

        """

        pp = cls(pt=Point.from_data(data['point']),
                 layer_height=data['layer_height'],
                 mesh_normal=Vector.from_data(data['mesh_normal']))

        pp.up_vector = Vector.from_data(data['up_vector'])
        pp.frame = Frame.from_data(data['frame'])

        pp.extruder_toggle = data['extruder_toggle']
        pp.velocity = data['velocity']
        pp.wait_time = data['wait_time']
        pp.blend_radius = data['blend_radius']

        pp.closest_support_pt = Point.from_data(data['closest_support_pt'])
        pp.distance_to_support = data['distance_to_support']

        pp.is_feasible = data['is_feasible']

        pp.attributes = data['attributes']
        return pp


if __name__ == "__main__":
    pass
