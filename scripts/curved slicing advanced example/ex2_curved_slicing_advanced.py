import os
from compas.datastructures import Mesh
import logging
import compas_slicer.utilities as utils
from compas_slicer.slicers import InterpolationSlicer
from compas_slicer.post_processing import simplify_paths_rdp_igl
from compas_slicer.pre_processing import InterpolationSlicingPreprocessor
from compas_slicer.pre_processing import create_mesh_boundary_attributes
from compas_slicer.print_organization import InterpolationPrintOrganizer
from compas_slicer.print_organization import set_extruder_toggle
from compas_slicer.print_organization import add_safety_printpoints, set_wait_time_on_sharp_corners
from compas_slicer.print_organization import smooth_printpoints_up_vectors, set_blend_radius
from compas_slicer.post_processing import generate_brim, seams_smooth
import time, math

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data_advanced_example')
OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
OBJ_INPUT_NAME = os.path.join(DATA_PATH, 'connection.obj')

REGION_SPLIT = True
SLICER = True
PRINT_ORGANIZER = True


def main():
    start_time = time.time()

    avg_layer_height = 4.0
    parameters = {
        'avg_layer_height': avg_layer_height,  # controls number of curves that will be generated
        'min_layer_height': avg_layer_height * 0.5,
        'max_layer_height': avg_layer_height * 2.00,
        'uneven_upper_targets_offset': 0,
        'target_HIGH_smooth_union': [True, [25.0]],  # on/off, blend radius
    }

    ### --- Load initial_mesh
    mesh = Mesh.from_obj(os.path.join(DATA_PATH, OBJ_INPUT_NAME))

    # --- Load targets (boundaries)
    low_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryLOW.json')
    high_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryHIGH.json')
    create_mesh_boundary_attributes(mesh, low_boundary_vs, high_boundary_vs)

    # --- Create pre-processor
    preprocessor = InterpolationSlicingPreprocessor(mesh, parameters, DATA_PATH)
    preprocessor.create_compound_targets()
    preprocessor.targets_laplacian_smoothing(iterations=4, strength=0.05)

    #########################################
    # --- region split
    if REGION_SPLIT:
        # --- ADVANCED slicing with region split
        g_eval = preprocessor.create_gradient_evaluation(target_1=preprocessor.target_LOW,
                                                         target_2=preprocessor.target_HIGH,
                                                         save_output=True)
        preprocessor.find_critical_points(g_eval, output_filenames=['minima.json', 'maxima.json', 'saddles.json'])
        preprocessor.region_split(save_split_meshes=True)  # split mesh regions on saddle points
        # utils.interrupt()

    #########################################
    # --- slicing
    if SLICER:

        slicers = []
        filenames = utils.get_all_files_with_name('split_mesh_', '.json', OUTPUT_PATH)
        split_meshes = [Mesh.from_json(os.path.join(OUTPUT_PATH, filename)) for filename in filenames]
        for i, split_mesh in enumerate(split_meshes):
            preprocessor_split = InterpolationSlicingPreprocessor(split_mesh, parameters, DATA_PATH)
            preprocessor_split.create_compound_targets()
            preprocessor_split.create_gradient_evaluation(norm_filename='gradient_norm_%d.json' % i,
                                                          g_filename='gradient_%d.json' % i,
                                                          target_1=preprocessor_split.target_LOW,
                                                          target_2=preprocessor_split.target_HIGH)

            slicer = InterpolationSlicer(split_mesh, preprocessor_split, parameters)
            if i == 3:
                slicer.n_multiplier = 0.85
            slicer.slice_model()

            if i == 0:
                generate_brim(slicer, layer_width=3.0, number_of_brim_offsets=5)

            seams_smooth(slicer, smooth_distance=0.1)
            simplify_paths_rdp_igl(slicer, threshold=0.25)
            utils.save_to_json(slicer.to_data(), OUTPUT_PATH, 'curved_slicer_%d.json' % i)
            slicers.append(slicer)

        # utils.interrupt()

    #########################################
    # --- print organization
    if PRINT_ORGANIZER:
        filenames = utils.get_all_files_with_name('curved_slicer_', '.json', OUTPUT_PATH)
        slicers = [InterpolationSlicer.from_data(utils.load_from_json(OUTPUT_PATH, filename)) for filename in filenames]
        for i, slicer in enumerate(slicers):
            print_organizer = InterpolationPrintOrganizer(slicer, parameters, DATA_PATH)
            print_organizer.create_printpoints()
            set_extruder_toggle(print_organizer, slicer)
            set_blend_radius(print_organizer)
            add_safety_printpoints(print_organizer, z_hop=10.0)
            smooth_printpoints_up_vectors(print_organizer, strength=0.5, iterations=10)
            set_wait_time_on_sharp_corners(print_organizer, threshold=0.5 * math.pi, wait_time=0.2)

            # --- Save printpoints dictionary to json file
            printpoints_data = print_organizer.output_printpoints_dict()
            utils.save_to_json(printpoints_data, OUTPUT_PATH, 'out_printpoints_flat_%d.json' % i)

            printpoints_data = print_organizer.output_nested_printpoints_dict()
            utils.save_to_json(printpoints_data, OUTPUT_PATH, 'out_printpoints_nested_%d.json' % i)

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")


if __name__ == "__main__":
    main()
