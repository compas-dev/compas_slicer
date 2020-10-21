import os
from compas.datastructures import Mesh
import logging
from compas_slicer.utilities import load_from_json, save_to_json
from compas_slicer.slicers import CurvedSlicer
from compas_slicer.post_processing import simplify_paths_rdp

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)

# DATA_PATH = os.path.join(os.path.dirname(__file__), 'data_basic_example')
# OBJ_INPUT_NAME = os.path.join(DATA_PATH, 'vase.obj')

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data_advanced_example')
OBJ_INPUT_NAME = os.path.join(DATA_PATH, 'connection.obj')

if __name__ == "__main__":
    ### --- Load initial_mesh
    mesh = Mesh.from_obj(os.path.join(DATA_PATH, OBJ_INPUT_NAME))

    ### --- Load targets (boundaries)
    low_boundary_vs = load_from_json(DATA_PATH, 'boundaryLOW.json')
    high_boundary_vs = load_from_json(DATA_PATH, 'boundaryHIGH.json')

    parameters = {
        'create_intermediary_outputs': True,
        'evaluate_scalar_field': True,
        'avg_layer_height': 5.0
    }

    ### --- slicing
    slicer = CurvedSlicer(mesh, low_boundary_vs, high_boundary_vs, DATA_PATH, parameters)
    slicer.slice_model()  # compute contours
    simplify_paths_rdp(slicer, threshold=1.0)
    slicer.printout_info()
    save_to_json(slicer.to_data(), DATA_PATH, 'curved_slicer.json')

    # # ### --- Print organizer
    # parameters = {
    #     'min_layer_height': 0.1,
    #     'max_layer_height': 50.0, #2.0,
    #     'layer_heights_smoothing': [False, 3, 0.5],  # boolean, iterations, strength
    #     'up_vectors_smoothing': [False, 3, 0.5]  # boolean, iterations, strength
    # }
    #
    # print_organizer = CurvedPrintOrganizer(slicer, parameters, DATA_PATH)
    # print_organizer.create_printpoints(mesh)
    # print_organizer.set_extruder_toggle()
    # print_organizer.add_safety_printpoints(z_hop=20)
    # print_organizer.set_linear_velocity()
    #
    # ### --- Save printpoints dictionary to json file
    # printpoints_data = print_organizer.output_printpoints_dict()
    # save_to_json(printpoints_data, DATA_PATH, 'out_printpoints.json')

    # ### ----- Visualize
    # viewer = ObjectViewer()
    # slicer.visualize_on_viewer(viewer, visualize_mesh=False, visualize_paths=True)
    # # print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)
    # viewer.update()
    # viewer.show()
