import os
from compas.datastructures import Mesh
from compas.geometry import Point

from compas_slicer.slicers import PlanarSlicer
from compas_slicer.slicers.post_processing import unify_paths_orientation
from compas_slicer.slicers.post_processing import seams_align, sort_per_segment, seams_smooth, generate_brim
from compas_slicer.print_organization import PrintOrganizer
from compas_slicer.utilities import save_to_json
from compas_viewers.objectviewer import ObjectViewer
from compas_slicer.slicers.post_processing import simplify_paths_rdp
from compas_slicer.slicers.pre_processing import move_mesh_to_point
import time

######################## Logging
import logging

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

### --- Data paths
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
OBJ_INPUT_NAME = os.path.join(DATA_PATH, 'simple_vase.obj')
OUTPUT_FILE = 'out_printpoints.json'

start_time = time.time()


def main():
    print(DATA_PATH)
    ### --- Load stl
    compas_mesh = Mesh.from_obj(OBJ_INPUT_NAME)
    ### --- Move to origin
    move_mesh_to_point(compas_mesh, Point(0, 0, 0))

    ### --- Slicer
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_compas", layer_height=5.0)
    slicer.slice_model()

    sort_per_segment(slicer, max_layers_per_segment=False, threshold=slicer.layer_height * 1.6)
    simplify_paths_rdp(slicer, threshold=0.2)
    generate_brim(slicer, layer_width=3.0, number_of_brim_paths=4)

    seams_align(slicer, align_with="next_path")
    seams_smooth(slicer, 10)
    unify_paths_orientation(slicer)

    slicer.printout_info()

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")

    viewer = ObjectViewer()
    viewer.view.use_shaders = False
    slicer.visualize_on_viewer(viewer, visualize_mesh=False, visualize_paths=True)

    save_to_json(slicer.to_data(), DATA_PATH, 'slicer_data.json')

    ### --- Fabrication - related information

    print_organizer = PrintOrganizer(slicer, compas_mesh, extruder_toggle_type="off_when_travel")

    per_layer_velocities = [0.05 for _ in range(print_organizer.number_of_layers())]
    per_layer_velocities[0], per_layer_velocities[1] = 0.025, 0.025
    print_organizer.set_linear_velocity(velocity_type="per_layer",
                                        per_layer_velocities=per_layer_velocities)
    # print_organizer.add_safety_printpoints(z_hop=20)

    print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)

    robotic_commands = print_organizer.generate_printpoints_dict()
    save_to_json(robotic_commands, DATA_PATH, OUTPUT_FILE)

    viewer.update()
    viewer.show()


if __name__ == "__main__":
    main()
