import compas
import compas_am
import os, sys
from compas.datastructures import Mesh
from compas_plotters import MeshPlotter

from compas_am.slicing.slicer import Slicer
from compas_am.input.input_geometry import InputGeometry
from compas_am.fabrication.fabrication_sequence import Fabrication_sequence
from compas_am.fabrication.machine_model import MachineModel
from compas_am.positioning.center_mesh_on_build_platform import center_mesh_on_build_platform

######################## Logging
import logging
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_FILE = os.path.abspath(os.path.join(DATA, 'eight_eight.stl'))
OUTPUT_FILE = os.path.abspath(os.path.join(DATA, 'gcode_test.gcode'))

def main():

    ### --- Load stl
    compas_mesh = Mesh.from_stl(INPUT_FILE)

    ### --- Get machine model
    machine_model = MachineModel(printer_model = "FDM_Prusa_i3_mk2")
    machine_data = machine_model.get_machine_data()

    ### --- Center mesh on build platform
    compas_mesh = center_mesh_on_build_platform(compas_mesh, machine_data)

    ### --- Slicer
    slicer = Slicer(compas_mesh, slicer_type = "planar_meshcut", layer_height = 2.0)

    slicer.slice_model(create_contours = True, create_infill = False, create_supports = False)

    slicer.simplify_paths(method = "uniform", threshold = 0.2)

    # slicer.sort_paths(method = "shortest_path", max_attempts=1)

    paths = slicer.sort_paths(method = "shortest_path", max_layers_per_segment=False, max_attempts=0)
    
    fab_seq = Fabrication_sequence(paths, machine_model = None, fabrication_type = "fdm")
    
    fab_seq.save_commands_to_gcode(OUTPUT_FILE, 
                                   extruder_temp = 210, 
                                   bed_temp = 60, 
                                   print_speed = 50)

    slicer.save_contours_to_json(path = DATA, name = "eight_eight_contours.json")

    # slicer.align_seams(method = "seams_align")

    slicer.printout_info()


if __name__ == "__main__":
    main()