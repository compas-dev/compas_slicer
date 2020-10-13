import os
from compas.datastructures import Mesh
from compas.geometry import Point, Frame

from compas_slicer.utilities import save_to_json
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.functionality import generate_brim
from compas_slicer.functionality import spiralize_contours
from compas_slicer.functionality import seams_align
from compas_slicer.functionality import seams_smooth, unify_paths_orientation
from compas_slicer.fabrication import RoboticPrintOrganizer
from compas_slicer.fabrication import RobotPrinter
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
# MODEL = 'simple_vase.stl'
MODEL = 'simple_vase.stl'
OUTPUT_FILE = 'fabrication_commands.json'

start_time = time.time()

def main():
    ### --- Load stl
    compas_mesh = Mesh.from_stl(os.path.join(DATA, MODEL))

    ### --- Move to origin
    move_mesh_to_point(compas_mesh, Point(0,0,0))

    ### --- Slicer
    # try out different slicers by changing the slicer_type
    # options: 'planar_compas', 'planar_numpy', 'planar_meshcut', 'planar_cgal'
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_cgal", layer_height=3.0)
    slicer.slice_model()

    ### --- Generate brim
    generate_brim(slicer, layer_width=3.0, number_of_brim_paths=3)

    ### --- Align the seams between layers
    # options: 'next_path', 'x_axis', 'y_axis', 'origin', 'Point(x,y,z)'
    seams_align(slicer, align_with='x_axis')

    ### --- Make sure all paths are looking in the same direction
    unify_paths_orientation(slicer)

    ### --- Simplify the printpaths by removing points with a certain threshold
    # change the threshold value to remove more or less points
    simplify_paths_rdp(slicer, threshold=0.4)

    ### --- Smooth the seams between layers
    # change the smooth_distance value to achieve smoother, or more abrupt seams
    seams_smooth(slicer, smooth_distance=10)

    # WIP
    # spiralize_contours(slicer)

    ### --- Prints out the info of the slicer
    slicer.printout_info()

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")

    viewer = ObjectViewer()
    viewer.view.use_shaders = False
    slicer.visualize_on_viewer(viewer)

    save_to_json(slicer.to_data(), DATA, 'slicer_data.json')

    ### --- Visualize using the compas_viewer
    # viewer = ObjectViewer()
    # viewer.view.use_shaders = False
    # slicer.visualize_on_viewer(viewer, visualize_mesh=False, visualize_paths=True)

    ### --- Fabrication
    robot_printer = RobotPrinter('UR5')
    robot_printer.attach_endeffector(FILENAME=os.path.join(DATA, 'plastic_extruder.obj'),
                                     frame=Frame(point=[0.153792, -0.01174, -0.03926],
                                                 xaxis=[1, 0, 0],
                                                 yaxis=[0, 1, 0]))
    # robot_printer.printout_info()

    ### --- Initializes a robotic printing process
    # options extruder_toggle_type: always_on, always_off, off_when_travel
    print_organizer = RoboticPrintOrganizer(slicer, machine_model=robot_printer,
                                            extruder_toggle_type="always_on")

    # print_organizer.add_safety_printpoints(z_hop=20)

    ### --- Sets the linear velocity
    # options velocity_type: constant, per_layer, matching_layer_height, matching_overhang
    print_organizer.set_linear_velocity(velocity_type="constant", v=35)

    # print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)

    ### --- Create robotic commands and save to json file
    robotic_commands = print_organizer.generate_robotic_commands_dict()
    save_to_json(robotic_commands, DATA, OUTPUT_FILE)

    viewer.update()
    viewer.show()

if __name__ == "__main__":
    main()
