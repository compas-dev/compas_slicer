import logging
from compas.geometry import Vector, normalize_vector
from compas_slicer.geometry import PrintPoint
import compas_slicer.utilities as utils

logger = logging.getLogger('logger')

__all__ = ['BaseBoundary']


class BaseBoundary:
    """
    The BaseBoundary is like a fake initial layer that supports the first path of the segment.
    This is useful, because for our computations we need to have a support layer for evey path.
    The first path has as support the Base Boundary, and every other path has its previous path.

    Attributes
    ----------
    mesh :
    points :
    override_vector :
    """

    def __init__(self, mesh, points, override_vector=None):
        self.mesh = mesh
        self.points = points
        self.override_vector = override_vector
        closest_fks, projected_pts = utils.pull_pts_to_mesh_faces(self.mesh, [pt for pt in self.points])
        self.normals = [Vector(*self.mesh.face_normal(fkey)) for fkey in closest_fks]

        if self.override_vector:
            self.up_vectors = [self.override_vector for p in self.points]
        else:
            self.up_vectors = self.get_up_vectors()

        self.printpoints = [PrintPoint(pt=pt,  # Create fake print points
                                       layer_height=1.0,
                                       mesh_normal=self.normals[i]) for i, pt in enumerate(self.points)]

        for i, pp in enumerate(self.printpoints):
            pp.up_vector = self.up_vectors[i]

    def __repr__(self):
        return "<BaseBoundary object with %i points>" % len(self.points)

    def get_up_vectors(self):
        """ Finds the up_vectors of each point of the boundary. A smoothing step is also included. """
        up_vectors = []
        for i, p in enumerate(self.points):
            v1 = Vector.from_start_end(p, self.points[(i + 1) % len(self.points)])
            cross = v1.cross(self.normals[i])
            v = Vector(*normalize_vector(cross))
            if v[2] < 0:
                v.scale(-1)
            up_vectors.append(v)
        up_vectors = utils.smooth_vectors(up_vectors, strength=0.4, iterations=3)
        return up_vectors

    def to_data(self):
        """ Returns a dictionary with the data of the class. """
        return {"points": utils.point_list_to_dict(self.points),
                "up_vectors": utils.point_list_to_dict(self.up_vectors)}


if __name__ == "__main__":
    pass
