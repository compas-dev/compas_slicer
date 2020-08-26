import compas
import compas_slicer
import os
from compas.datastructures import Mesh
from compas_plotters import MeshPlotter
from compas_slicer.polyline_simplification import simplify_paths_rdp
import compas_slicer.polyline_simplification.simplify_paths_curvature as simplify_paths_curvature
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.sorting import sort_per_segment, sort_per_shortest_path_mlrose
from compas_slicer.sorting import align_seams

from compas_slicer.fabrication import RoboticPrintOrganizer
from compas_slicer.fabrication import RobotPrinter
from compas_slicer.fabrication import Material

from compas.geometry import Frame

import time

######################## Logging
import logging
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = os.path.join(os.path.dirname(__file__), 'data')
FILE = os.path.join(DATA, 'branches_16.stl')
OUTPUT_FILE = os.path.join(DATA, 'fabrication_commands.json')

start_time = time.time()

def main():
    ### --- Load stl
    compas_mesh = Mesh.from_stl(FILE)

    ### --- Slicer
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_cgal", layer_height=100.0)
    slicer.slice_model(create_contours=True, create_infill=False, create_supports=False)
    slicer.generate_brim(layer_width=2, number_of_brim_layers=4)
    slicer.printout_info()

    simplify_paths_rdp(slicer, threshold=0.2)
    sort_per_shortest_path_mlrose(slicer, max_attempts=1)
    align_seams(slicer, seam_orientation="next_contour")

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")

    slicer.to_json(DATA, 'slicer_data.json')

    slicer.layers_to_json(DATA, 'slicer_data_layers.json')
    
    robot_printer = RobotPrinter('UR5')
    material_PLA = Material('PLA')

    print_organizer = RoboticPrintOrganizer(slicer, machine_model=robot_printer, material=material_PLA)
    print_organizer.generate_z_hop(z_hop=20)
    print_organizer.generate_commands()

    print_organizer.set_extruder_toggle(extruder_toggle="off_when_travel_zhop")

    
    print_organizer.save_commands_to_json(OUTPUT_FILE)

if __name__ == "__main__":
    main()
