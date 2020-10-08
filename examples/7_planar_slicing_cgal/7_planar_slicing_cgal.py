import os
from compas.datastructures import Mesh
from compas.geometry import Point

from compas_slicer.utilities import save_to_json
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.slicers import spiralize_contours
from compas_slicer.functionality import sort_per_shortest_path_mlrose
from compas_slicer.functionality import align_seams
from compas_slicer.fabrication import RoboticPrintOrganizer
from compas_slicer.fabrication import RobotPrinter
from compas_slicer.fabrication import Material
from compas_viewers.objectviewer import ObjectViewer
from compas_slicer.functionality import move_mesh_to_point, simplify_paths_rdp
import time

######################## Logging
import logging
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

### --- Data paths
DATA = os.path.join(os.path.dirname(__file__), 'data')
MODEL = 'simple_vase.stl'
OUTPUT_FILE = 'fabrication_commands.json'

start_time = time.time()

def main():
    ### --- Load stl
    compas_mesh = Mesh.from_stl(os.path.join(DATA, MODEL))
    ### --- Move to origin
    move_mesh_to_point(compas_mesh, Point(0,0,0))

    ### --- Slicer
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_cgal", layer_height=7.0)
    slicer.slice_model()
    # slicer.generate_brim(layer_width=3.0, number_of_brim_paths=3)

    # simplify_paths_rdp(slicer, threshold=0.2)
    align_seams(slicer, seam_orientation="x_axis")

    # WIP
    # spiralize_contours(slicer)

    slicer.printout_info()

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")

    viewer = ObjectViewer()
    viewer.view.use_shaders = False
    slicer.visualize_on_viewer(viewer, visualize_mesh=False, visualize_paths=True)

    # slicer.path_collections_to_json(DATA, 'slicer_data_layers.json')

    ### --- Fabrication
    robot_printer = RobotPrinter('UR5')
    material_PLA = Material('PLA')

    print_organizer = RoboticPrintOrganizer(slicer, machine_model=robot_printer, material=material_PLA,
                                            extruder_toggle_type="off_when_travel")

    # print_organizer.add_z_hop_printpoints(z_hop=20)

    print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)

    robotic_commands = print_organizer.generate_robotic_commands_dict()
    save_to_json(robotic_commands, DATA, OUTPUT_FILE)

    viewer.update()
    viewer.show()

if __name__ == "__main__":
    main()
