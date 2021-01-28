import logging
from compas.geometry import Plane, Point, Vector, distance_point_plane
from compas.datastructures import Mesh
import os
import compas_slicer.utilities as slicer_utils
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.slicers import ScalarFieldSlicer
from compas_slicer.pre_processing.curved_slicing_preprocessing.geodesics import get_igl_EXACT_geodesic_distances
import compas_slicer.utilities as utils
from compas_slicer.pre_processing.curved_slicing_preprocessing import GradientEvaluation
from compas_slicer.print_organization import ScalarFieldPrintOrganizer

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
    slicer = ScalarFieldSlicer(mesh, u, no_of_isocurves=20)
    slicer.slice_model()
    slicer_utils.save_to_json(slicer.to_data(), OUTPUT_PATH, 'isocontours.json')
    simplify_paths_rdp(slicer, threshold=0.8)

    # create printpoints
    print_organizer = ScalarFieldPrintOrganizer(slicer, parameters={}, DATA_PATH=DATA_PATH)
    print_organizer.create_printpoints()
    printpoints_data = print_organizer.output_printpoints_dict()
    utils.save_to_json(printpoints_data, OUTPUT_PATH, 'out_printpoints.json')

    # add gradient information on vertices
    mesh.update_default_vertex_attributes({'scalar_field': 0.0})
    for i, (v_key, data) in enumerate(mesh.vertices(data=True)):
        data['scalar_field'] = u[i]
    g_evaluation = GradientEvaluation(mesh, DATA_PATH)
    g_evaluation.compute_gradient()
    g_evaluation.compute_gradient_norm()

    utils.save_to_json(g_evaluation.vertex_gradient_norm, OUTPUT_PATH, 'v_gradient_norm.json')
    utils.save_to_json(utils.point_list_to_dict(g_evaluation.vertex_gradient), OUTPUT_PATH, 'v_gradient.json')

    mesh.update_default_vertex_attributes({'v_gradient': 0.0})
    mesh.update_default_vertex_attributes({'v_gradient_norm': 0.0})
    mesh.update_default_vertex_attributes({'f_gradient': 0.0})
    mesh.update_default_vertex_attributes({'f_gradient_norm': 0.0})
    for i, (v_key, data) in enumerate(mesh.vertices(data=True)):
        data['v_gradient'] = g_evaluation.vertex_gradient[i]
        data['v_gradient_norm'] = g_evaluation.vertex_gradient_norm[i]
        data['f_gradient'] = g_evaluation.vertex_gradient[i]
        data['f_gradient_norm'] = g_evaluation.vertex_gradient_norm[i]

    # transfer to printpoints
    print_organizer.transfer_attributes_to_printpoints()

    reconstructed_v_grad = []
    reconstructed_v_grad_norm = []
    reconstructed_f_grad = []
    reconstructed_f_grad_norm = []

    for i, layer in enumerate(print_organizer.slicer.layers):
        layer_key = 'layer_%d' % i
        for j, path in enumerate(layer.paths):
            path_key = 'path_%d' % j
            for pp in print_organizer.printpoints_dict[layer_key][path_key]:
                reconstructed_v_grad.append(pp.attributes['v_gradient'])
                reconstructed_v_grad_norm.append(pp.attributes['v_gradient_norm'])
                reconstructed_f_grad.append(pp.attributes['f_gradient'])
                reconstructed_f_grad_norm.append(pp.attributes['f_gradient_norm'])

    utils.save_to_json(reconstructed_v_grad_norm, OUTPUT_PATH, 'reconstructed_v_gradient_norm.json')
    utils.save_to_json(utils.point_list_to_dict(reconstructed_v_grad), OUTPUT_PATH, 'reconstructed_v_gradient.json')
    utils.save_to_json(reconstructed_f_grad_norm, OUTPUT_PATH, 'reconstructed_f_gradient_norm.json')
    utils.save_to_json(utils.point_list_to_dict(reconstructed_f_grad), OUTPUT_PATH, 'reconstructed_f_gradient.json')
