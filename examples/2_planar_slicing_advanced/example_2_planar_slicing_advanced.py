import os
from compas.datastructures import Mesh
from compas.geometry import Point, Frame

from compas_slicer.utilities import save_to_json
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.functionality import generate_brim
from compas_slicer.functionality import seams_align
from compas_slicer.functionality import seams_smooth
from compas_slicer.functionality import sort_per_shortest_path_mlrose
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
MODEL = 'branches_70.stl'
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
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_cgal", layer_height=100.0)
    slicer.slice_model()

    ### --- Generate brim    
    # generate_brim(slicer, layer_width=3.0, number_of_brim_paths=3)

    ### --- Simplify the printpaths by removing points with a certain threshold
    # change the threshold value to remove more or less points
    simplify_paths_rdp(slicer, threshold=0.2)
    
    # seams_align(slicer, seam_orientation="next_path")
    # seams_smooth(slicer, smooth_distance=5)
    
    # WIP
    # sort_per_shortest_path_mlrose(slicer)

    ### --- Prints out the info of the slicer
    slicer.printout_info()

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")

    ### --- Visualize using the compas_viewer
    viewer = ObjectViewer()
    viewer.view.use_shaders = False
    slicer.visualize_on_viewer(viewer, visualize_mesh=False, visualize_paths=True)

    ### --- Fabrication
    robot_printer = RobotPrinter('UR5')
    robot_printer.attach_endeffector(FILENAME=os.path.join(DATA, 'plastic_extruder.obj'),
                                     frame=Frame(point=[0.153792, -0.01174, -0.03926],
                                                 xaxis=[1, 0, 0],
                                                 yaxis=[0, 1, 0]))
    # robot_printer.printout_info()

    print_organizer = RoboticPrintOrganizer(slicer, machine_model=robot_printer,
                                            extruder_toggle_type="off_when_travel")

    ### --- Adds a z-hop value to the print
    print_organizer.add_z_hop_printpoints(z_hop=20)
    
    # print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)

    ### --- Sets the linear velocity
    print_organizer.set_linear_velocity(velocity_type="constant", v=25)

    robotic_commands = print_organizer.generate_robotic_commands_dict()
    save_to_json(robotic_commands, DATA, OUTPUT_FILE)

    # viewer.update()
    # viewer.show()

if __name__ == "__main__":
    main()
