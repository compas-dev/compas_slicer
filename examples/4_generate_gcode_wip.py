import compas
import compas_am
import os, sys
from compas.datastructures import Mesh
from compas_plotters import MeshPlotter

from compas_am.slicing.slicer import Slicer
from compas_am.input.input_geometry import InputGeometry
from compas_am.fabrication.fabrication_sequence import Fabrication_sequence
from compas_am.fabrication.machine_model import Printer
from compas_am.positioning.center_mesh_on_build_platform import center_mesh_on_build_platform

######################## Logging
import logging
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_FILE = os.path.abspath(os.path.join(DATA, 'box.stl'))
OUTPUT_FILE = os.path.abspath(os.path.join(DATA, 'gcode_test.gcode'))

def main():

    ### --- Load stl
    compas_mesh = Mesh.from_stl(INPUT_FILE)

    ### --- Get machine model
    machine_model = Printer("FDM_Prusa_i3_mk2")
    machine_dimensions = machine_model.get_machine_dimensions()
    machine_model.printout_info()

    ### --- Center mesh on build platform
    compas_mesh = center_mesh_on_build_platform(compas_mesh, machine_dimensions)

    ### --- Slicer
    slicer = Slicer(compas_mesh, slicer_type = "planar_meshcut", layer_height = 12.0)

    slicer.slice_model(create_contours = True, create_infill = False, create_supports = False)

    slicer.simplify_paths(method = "uniform", threshold = 0.2)

    slicer.printout_info()

    # slicer.sort_paths(method = "shortest_path", max_attempts=1)

    paths = slicer.sort_paths(method = "shortest_path", max_layers_per_segment=False, max_attempts=0)
    
    fab_seq = Fabrication_sequence(paths, machine_model = machine_model)
    
    fab_seq.save_commands_to_gcode(OUTPUT_FILE)

    


    


if __name__ == "__main__":
    main()