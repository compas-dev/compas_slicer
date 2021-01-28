import logging
from compas.geometry import Plane, Point, Vector, distance_point_plane
from compas.datastructures import Mesh
import os
import compas_slicer.utilities as slicer_utils
from compas_slicer.slicers import ScalarFieldSlicer
from compas_slicer.pre_processing.curved_slicing_preprocessing.geodesics import get_igl_EXACT_geodesic_distances
import compas_slicer.utilities as utils
import math
from compas_slicer.print_organization import PlanarPrintOrganizer

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
OUTPUT_PATH = slicer_utils.get_output_directory(DATA_PATH)
MODEL = '_mesh.obj'

if __name__ == '__main__':
    # load mesh
    mesh = Mesh.from_obj(os.path.join(DATA_PATH, MODEL))

    # Create scalar field
    plane = Plane(Point(0, 0, -30), Vector(0.0, 0.5, 0.5))
    v_coords = [mesh.vertex_coordinates(v_key, axes='xyz') for v_key in mesh.vertices()]
    u = [distance_point_plane(v, plane) for v in v_coords]

    # generate contours of scalar field
    contours = ScalarFieldSlicer(mesh, u, no_of_isocurves=20)
    contours.slice_model()
    slicer_utils.save_to_json(contours.to_data(), OUTPUT_PATH, 'isocontours.json')

    print_organizer = PlanarPrintOrganizer(contours)
    print_organizer.create_printpoints()

    print_organizer.transfer_attributes_to_printpoints()

    for i, layer in enumerate(print_organizer.slicer.layers):
        layer_key = 'layer_%d' % i
        for j, path in enumerate(layer.paths):
            path_key = 'path_%d' % j
            for pp in print_organizer.printpoints_dict[layer_key][path_key]:
                print (pp.attributes)
