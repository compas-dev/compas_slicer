import os
from compas.datastructures import Mesh
from compas.geometry import Frame

from compas_slicer.functionality import sort_per_segment, sort_per_shortest_path_mlrose
from compas_slicer.functionality import seams_align
from compas_slicer.functionality import simplify_paths_rdp
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.fabrication import RoboticPrintOrganizer
from compas_slicer.fabrication import RobotPrinter

from compas_slicer.utilities import save_to_json
from compas_plotters import MeshPlotter
from compas_viewers.objectviewer import ObjectViewer

######################## Logging
import logging

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = 'data'
INPUT_FILE = os.path.abspath(os.path.join(DATA, 'box.stl'))
OUTPUT_FILE = os.path.abspath(os.path.join(DATA, 'commands.json'))


def main():
    ### --- Load stl
    compas_mesh = Mesh.from_stl(INPUT_FILE)

    ### --- Slicer
    slicer = PlanarSlicer(compas_mesh, slicer_type='planar_compas', layer_height=3.0)
    slicer.slice_model()
    slicer.printout_info()

    # simplify_paths_rdp(slicer, threshold=0.02)
    sort_per_shortest_path_mlrose(slicer, max_attempts=4)
    seams_align(slicer)

    ### --- Fabrication
    robot_printer = RobotPrinter('UR5')
    robot_printer.attach_endeffector(FILENAME=os.path.join(DATA, 'plastic_extruder.obj'),
                                     frame=Frame(point=[0.153792, -0.01174, -0.03926],
                                                 xaxis=[1, 0, 0],
                                                 yaxis=[0, 1, 0]))
    robot_printer.printout_info()

    print_organizer = RoboticPrintOrganizer(slicer, machine_model=robot_printer,
                                            extruder_toggle_type="always_on")

    robotic_commands = print_organizer.generate_robotic_commands_dict()
    save_to_json(robotic_commands, DATA, OUTPUT_FILE)

    ### ----- Visualize
    viewer = ObjectViewer()
    # slicer.visualize_on_viewer(viewer, visualize_mesh=True, visualize_paths=False)
    print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)
    viewer.update()
    viewer.show()


if __name__ == '__main__':
    main()
