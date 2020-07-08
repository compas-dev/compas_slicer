import os
from compas.datastructures import Mesh
from compas.geometry import Frame

from compas_slicer.sorting import sort_per_segment, sort_per_shortest_path_mlrose
from compas_slicer.sorting import align_seams
from compas_slicer.polyline_simplification import simplify_paths_rdp

from compas_slicer.slicers import PlanarSlicer
from compas_slicer.fabrication import RoboticPrintOrganizer
from compas_slicer.fabrication import RobotPrinter
from compas_slicer.fabrication import Material

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
    slicer = PlanarSlicer(compas_mesh, slicer_type='planar_meshcut', layer_height=10.0)
    slicer.slice_model(create_contours=True, create_infill=False, create_supports=False)
    slicer.printout_info()

    simplify_paths_rdp(slicer, threshold=0.2)
    sort_per_shortest_path_mlrose(slicer, max_attempts=4)
    align_seams(slicer)

    ### --- Fabrication
    robot_printer = RobotPrinter('UR5')
    robot_printer.attach_endeffector(FILENAME=os.path.join(DATA, 'plastic_extruder.obj'),
                                     frame=Frame(point=[0.153792, -0.01174, -0.03926],
                                                 xaxis=[1, 0, 0],
                                                 yaxis=[0, 1, 0]))
    robot_printer.printout_info()

    material_PLA = Material('PLA')
    material_PLA.printout_info()

    print_organizer = RoboticPrintOrganizer(slicer, machine_model=robot_printer, material=material_PLA)
    print_organizer.generate_commands()
    print_organizer.save_commands_to_json(OUTPUT_FILE)


if __name__ == '__main__':
    main()
