import os
from compas.datastructures import Mesh
import logging
from compas.geometry import Point
import compas_slicer.utilities as utils
from compas_slicer.geometry import PrintPoint
from compas_slicer.slicers import CurvedSlicer, BaseSlicer
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.pre_processing import CurvedSlicingPreprocessor
from compas_slicer.pre_processing import create_mesh_boundary_attributes
from compas_slicer.print_organization import CurvedPrintOrganizer
from compas_viewers.objectviewer import ObjectViewer
from compas_slicer.pre_processing import move_mesh_to_point
from compas_slicer.print_organization.print_organization_utilities import analysis

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data_advanced_example')
OBJ_INPUT_NAME = os.path.join(DATA_PATH, 'connection.obj')
# OBJ_INPUT_NAME = os.path.join(DATA_PATH, 'connection_HIGH_RES.obj')

REGION_SPLIT = True
SLICER = True
PRINT_ORGANIZER = True

if __name__ == "__main__":

    parameters = {
        'target_LOW_smooth': [True, 5],  # boolean, blend_radius
        'target_HIGH_smooth': [True, 5],  # boolean, blend_radius
        'create_intermediary_outputs': True,
        'avg_layer_height': 5.0,
        'min_layer_height': 0.1,
        'max_layer_height': 50.0,  # 2.0,
        'layer_heights_smoothing': [False, 3, 0.5],  # boolean, iterations, strength
        'up_vectors_smoothing': [False, 3, 0.5]  # boolean, iterations, strength
    }

    ### --- Load initial_mesh
    mesh = Mesh.from_obj(os.path.join(DATA_PATH, OBJ_INPUT_NAME))
    move_mesh_to_point(mesh, Point(0, 0, 0))

    # --- Load targets (boundaries)
    low_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryLOW.json')
    high_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryHIGH.json')
    create_mesh_boundary_attributes(mesh, low_boundary_vs, high_boundary_vs)

    # --- Create pre-processor
    preprocessor = CurvedSlicingPreprocessor(mesh, parameters, DATA_PATH)
    preprocessor.create_compound_targets()

    #########################################
    # --- slicing
    if REGION_SPLIT:
        # --- ADVANCED slicing with region split
        preprocessor.scalar_field_evaluation(output_filename='gradient_norm.json')
        preprocessor.find_critical_points(output_filenames=['minima.json', 'maxima.json', 'saddles.json'])
        preprocessor.region_split(save_split_meshes=True)  # split mesh regions on saddle points

    #########################################
    # --- slicing
    if SLICER:
        slicers = []
        filenames = utils.get_files_with_name('split_mesh_', '.json', DATA_PATH)
        split_meshes = [Mesh.from_json(os.path.join(DATA_PATH, filename)) for filename in filenames]
        for i, split_mesh in enumerate(split_meshes):
            preprocessor_split = CurvedSlicingPreprocessor(split_mesh, parameters, DATA_PATH)
            preprocessor_split.create_compound_targets()
            preprocessor_split.scalar_field_evaluation(output_filename='gradient_norm_%d.json' % i)

            slicer = CurvedSlicer(split_mesh, preprocessor_split, parameters, DATA_PATH)
            if i == 3:
                slicer.n_multiplier = 0.85
            slicer.slice_model()
            simplify_paths_rdp(slicer, threshold=1.0)
            utils.save_to_json(slicer.to_data(), DATA_PATH, 'curved_slicer_%d.json' % i)
            slicers.append(slicer)
        # utils.interrupt()

    #########################################
    # --- print organization
    if PRINT_ORGANIZER:
        filenames = utils.get_files_with_name('curved_slicer_', '.json', DATA_PATH)
        slicers = [BaseSlicer.from_data(utils.load_from_json(DATA_PATH, filename)) for filename in filenames]
        for i, slicer in enumerate(slicers):
            print_organizer = CurvedPrintOrganizer(slicer, parameters, DATA_PATH)
            print_organizer.create_printpoints(mesh)
            # print_organizer.set_extruder_toggle()
            # print_organizer.add_safety_printpoints(z_hop=20)
            # print_organizer.set_linear_velocity()

            ### --- Save printpoints dictionary to json file
            printpoints_data = print_organizer.output_printpoints_dict()
            utils.save_to_json(printpoints_data, DATA_PATH, 'out_printpoints_%d.json' % i)
