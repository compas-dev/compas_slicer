import compas
import compas_am
import os, sys
from compas.datastructures import Mesh
from compas.geometry import Frame
from compas_plotters import MeshPlotter

from compas_am.slicing import Slicer
from compas_am.fabrication import RoboticPrintOrganizer
from compas_am.fabrication import RobotPrinter
from compas_am.fabrication import Material

######################## Logging
import logging

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_FILE = os.path.abspath(os.path.join(DATA, 'box.stl'))
OUTPUT_FILE = os.path.abspath(os.path.join(DATA, 'commands.json'))


def main():
    ### --- Load stl
    compas_mesh = Mesh.from_stl(INPUT_FILE)

    ### --- Slicer
    slicer = Slicer(compas_mesh, slicer_type='planar_meshcut', layer_height=10.0)

    slicer.slice_model(create_contours=True, create_infill=False, create_supports=False)

    slicer.simplify_paths(method='uniform', threshold=0.2)

    slicer.printout_info()

    paths = slicer.sort_paths(method='shortest_path', max_layers_per_segment=False, max_attempts=0)

    ### --- Fabrication
    robot_printer = RobotPrinter('UR5')
    robot_printer.attach_endeffector(FILENAME=os.path.join(DATA, 'robot_printer/plastic_extruder.obj'),
                                     frame=Frame(point=[0.153792, -0.01174, -0.03926],
                                                 xaxis=[1, 0, 0],
                                                 yaxis=[0, 1, 0]))

    material_PLA = Material('PLA')

    print_organizer = RoboticPrintOrganizer(paths, machine_model=robot_printer, material=material_PLA)

    print_organizer.save_commands_to_json(OUTPUT_FILE)


if __name__ == '__main__':
    main()
