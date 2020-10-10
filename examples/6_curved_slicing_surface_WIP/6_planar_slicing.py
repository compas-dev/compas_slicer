import os
from compas.datastructures import Mesh
from compas.geometry import Point, Frame

from compas_slicer.utilities import save_to_json
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.functionality import sort_per_shortest_path_mlrose
from compas_slicer.functionality import seams_align, sort_per_segment
from compas_slicer.fabrication import RoboticPrintOrganizer
from compas_slicer.fabrication import RobotPrinter
from compas_slicer.utilities import save_to_json
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
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
OBJ_INPUT_NAME = os.path.join(DATA_PATH, 'vase.obj')
OUTPUT_FILE = 'fabrication_commands.json'

start_time = time.time()


def main():
    ### --- Load stl
    compas_mesh = Mesh.from_obj(OBJ_INPUT_NAME)
    ### --- Move to origin
    move_mesh_to_point(compas_mesh, Point(0, 0, 0))

    ### --- Slicer
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_compas", layer_height=5.0)
    slicer.slice_model()

    sort_per_segment(slicer, max_layers_per_segment=False, threshold=slicer.layer_height * 1.6)
    simplify_paths_rdp(slicer, threshold=0.2)
    seams_align(slicer, seam_orientation="next_path")

    # WIP
    # spiralize_contours(slicer)

    slicer.printout_info()

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")

    viewer = ObjectViewer()
    viewer.view.use_shaders = False
    slicer.visualize_on_viewer(viewer, visualize_mesh=False, visualize_paths=True)

    save_to_json(slicer.to_data(), DATA, 'slicer_data_layers.json')

    ### --- Fabrication
    UR5_printer = RobotPrinter('UR5')
    UR5_printer.attach_endeffector(FILENAME=os.path.join(DATA, 'plastic_extruder.obj'),
                                   frame=Frame(point=[0.153792, -0.01174, -0.03926],
                                               xaxis=[1, 0, 0],
                                               yaxis=[0, 1, 0]))

    print_organizer = RoboticPrintOrganizer(slicer, machine_model=UR5_printer,
                                            extruder_toggle_type="off_when_travel")

    per_layer_velocities = [0.05 for _ in range(print_organizer.number_of_layers())]
    per_layer_velocities[0], per_layer_velocities[1] = 0.025, 0.025
    print_organizer.set_linear_velocity(velocity_type="per_layer",
                                        per_layer_velocities=per_layer_velocities)
    # print_organizer.add_z_hop_printpoints(z_hop=20)

    print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)

    robotic_commands = print_organizer.generate_robotic_commands_dict()
    save_to_json(robotic_commands, DATA, OUTPUT_FILE)

    viewer.update()
    viewer.show()


if __name__ == "__main__":
    main()
