import logging
from compas.geometry import Plane, Point, Vector, distance_point_plane
from compas.datastructures import Mesh
import os
import compas_slicer.utilities as slicer_utils
from compas_slicer.slicers import ScalarFieldSlicer
from compas_slicer.pre_processing.curved_slicing_preprocessing.geodesics import get_igl_EXACT_geodesic_distances
import compas_slicer.utilities as utils
import math

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
OUTPUT_PATH = slicer_utils.get_output_directory(DATA_PATH)
MODEL = '_mesh.obj'

if __name__ == '__main__':
    # load mesh
    mesh = Mesh.from_obj(os.path.join(DATA_PATH, MODEL))

    # ### --- Load targets (boundaries)
    # low_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryLOW.json')
    # high_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryHIGH.json')
    # d1 = get_igl_EXACT_geodesic_distances(mesh, low_boundary_vs)
    # d2 = get_igl_EXACT_geodesic_distances(mesh, high_boundary_vs)
    # u = [0.0 for _ in mesh.vertices()]
    # for i, _ in enumerate(mesh.vertices()):
    #     d = min(d1[i], d2[i])
    #     D = max(d1[i], d2[i])
    #     u[i] = d , d - D
    #     # if d1[i] < d2[i]:
    #     #     u[i] += 1.0
    # utils.save_to_json(u, OUTPUT_PATH, 'u.json')

    # Create scalar field
    plane = Plane(Point(0, 0, -30), Vector(0.0, 0.5, 0.5))
    v_coords = [mesh.vertex_coordinates(v_key, axes='xyz') for v_key in mesh.vertices()]
    u = [distance_point_plane(v, plane) for v in v_coords]

    # generate contours of scalar field
    contours = ScalarFieldSlicer(mesh, u, no_of_isocurves=40)
    contours.slice_model()
    slicer_utils.save_to_json(contours.to_data(), OUTPUT_PATH, 'isocontours.json')

    # PRINT ORGANIZATION DOES NOT WORK YET FOR SCALAR FIELD CONTOURS
