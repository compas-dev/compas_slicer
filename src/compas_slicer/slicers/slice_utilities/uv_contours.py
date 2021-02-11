from compas_slicer.slicers.slice_utilities import ContoursBase
from compas.geometry import intersection_line_line_xy, distance_point_point_xy, scale_vector, add_vectors


class UVContours(ContoursBase):
    def __init__(self, mesh, p1, p2):
        ContoursBase.__init__(self, mesh)  # initialize from parent class
        self.p1 = p1  # tuple (u,v); first point in uv domain defining the cutting line
        self.p2 = p2  # tuple (u,v); second point in uv domain defining the cutting line

    def uv(self, vkey):
        return self.mesh.vertex[vkey]['uv']

    def edge_is_intersected(self, v1, v2):
        """ Returns True if the edge v1,v2 intersects the line in the uv domain, False otherwise. """
        p = intersection_line_line_xy((self.p1, self.p2), (self.uv(v1), self.uv(v2)))
        if p:
            if is_point_on_line_xy(p, (self.uv(v1), self.uv(v2))):
                if is_point_on_line_xy(p, (self.p1, self.p2)):
                    return True
        return False

    def find_zero_crossing_data(self, v1, v2):
        """ Finds the position of the zero-crossing on the edge u,v. """
        p = intersection_line_line_xy((self.p1, self.p2), (self.uv(v1), self.uv(v2)))
        d1, d2 = distance_point_point_xy(self.uv(v1), p), distance_point_point_xy(self.uv(v2), p)
        if d1 + d2 > 0:
            vec = self.mesh.edge_vector(v1, v2)
            vec = scale_vector(vec, d1 / (d1 + d2))
            pt = add_vectors(self.mesh.vertex_coordinates(v1), vec)
            return pt


# utility function

def is_point_on_line_xy(c, line, epsilon=1e-6):
    """
    Not using the equivalent function of compas, because for some reason it always returns True.

    c: list that represents a point with 2 coordinates [x.y] of [x,y,0]
    line: (p1, p2) where each pt represents a point with 2 coordinates [x.y] of [x,y,0]
    """
    a, b = line[0], line[1]
    cross_product = (c[1] - a[1]) * (b[0] - a[0]) - (c[0] - a[0]) * (b[1] - a[1])

    if abs(cross_product) > epsilon:
        return False

    dot_product = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1]) * (b[1] - a[1])
    if dot_product < 0:
        return False

    squared_length_ba = (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1])
    if dot_product > squared_length_ba:
        return False

    return True


if __name__ == "__main__":
    pass
