import os
from compas.datastructures import Mesh
import logging
import compas_slicer.utilities.utils as utils
from compas_slicer.slicers import CurvedSlicer
from compas_plotters import MeshPlotter
from compas_slicer.fabrication import Material
from compas.geometry import Frame
from compas_slicer.fabrication import RobotPrinter
from compas_slicer.fabrication import RoboticPrintOrganizer

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)

########################
OBJ_INPUT_NAME = '_mesh.obj'
DATA_PATH = '1_surface/data'
########################

if __name__ == "__main__":
    ### --- Load initial_mesh
    mesh = Mesh.from_obj(os.path.join(DATA_PATH, OBJ_INPUT_NAME))

    ### --- Load boundaries
    low_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryLOW.json')
    high_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryHIGH.json')

    ### --- slicing
    slicer = CurvedSlicer(mesh, low_boundary_vs, high_boundary_vs, DATA_PATH)
    slicer.slice_model()  # generate contours

    slicer.to_json(DATA_PATH, 'curved_slicer.json')

    # slicer.generate_printpoints()  # generate printpoints with all necessary information for print



    ### --- Fabrication data
    # robot_printer = RobotPrinter('UR5')
    # robot_printer.attach_endeffector(FILENAME=os.path.join(os.path.dirname(__file__), '..',
    #                                                        'data', 'robot_printer/plastic_extruder.obj'),
    #                                  frame=Frame(point=[0.153792, -0.01174, -0.03926],
    #                                              xaxis=[1, 0, 0],
    #                                              yaxis=[0, 1, 0]))
    # robot_printer.printout_info()
    #
    # material_PLA = Material('PLA')
    # material_PLA.printout_info()

    ## remember to load json paths here

    # print_organizer = RoboticPrintOrganizer(slicer, machine_model=robot_printer, material=material_PLA)
    # print_organizer.generate_commands()
    # print_organizer.save_commands_to_json(OUTPUT_FILE)

    # ### ----- Visualize
    # plotter = MeshPlotter(mesh, figsize=(16, 10))
    # plotter.draw_edges(width=0.15)
    # plotter.draw_faces()
    # plotter.draw_lines(slicer.get_contour_lines_for_plotter(color=(255, 0, 0)))
    # plotter.show()
