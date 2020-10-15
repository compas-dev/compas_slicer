import os
from compas.datastructures import Mesh
import logging
import compas_slicer.utilities.utils as utils
from compas_slicer.slicers import CurvedSlicer, BaseSlicer
from compas_plotters import MeshPlotter
from compas_slicer.functionality import simplify_paths_rdp

from compas.geometry import Frame
from compas_viewers.objectviewer import ObjectViewer

from compas_viewers.objectviewer import ObjectViewer

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)

########################
# OBJ_INPUT_NAME = '_mesh.obj'
# DATA_PATH = 'data'
########################

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
OBJ_INPUT_NAME = os.path.join(DATA_PATH, 'vase.obj')

if __name__ == "__main__":
    ### --- Load initial_mesh
    mesh = Mesh.from_obj(os.path.join(DATA_PATH, OBJ_INPUT_NAME))

    ### --- Load targets (boundaries)
    low_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryLOW.json')
    high_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryHIGH.json')

    ### --- slicing
    slicer = CurvedSlicer(mesh, low_boundary_vs, high_boundary_vs, DATA_PATH, avg_layer_height = 3.0)
    slicer.slice_model()  # generate contours
    simplify_paths_rdp(slicer, threshold=0.6)

    slicer.printout_info()

    slicer.to_json(DATA_PATH, 'curved_slicer.json')

    # if create_print_organizer:
    #     # ### --- Print organizer
    #     slicer_data = utils.load_from_json(DATA_PATH, 'curved_slicer.json')
    #     slicer = BaseSlicer.from_data(slicer_data)
    #
    #     print_organizer = CurvedPrintOrganizer(slicer, machine_model=robot_printer,
    #                                                   material=material_PLA, DATA_PATH=DATA_PATH)
    #
    #     utils.save_to_json(print_organizer.to_data(), DATA_PATH, 'print_organizer.json')
    #
    #     # print_organizer.generate_commands()
    #     # print_organizer.save_commands_to_json(OUTPUT_FILE)


    ### ----- Visualize
    viewer = ObjectViewer()
    slicer.visualize_on_viewer(viewer, visualize_mesh=False, visualize_paths=True)
    # print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)
    viewer.update()
    viewer.show()