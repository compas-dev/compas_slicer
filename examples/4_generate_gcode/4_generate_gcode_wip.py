import os
from compas.datastructures import Mesh

from compas_slicer.slicers import PlanarSlicer
from compas_slicer.sorting import sort_per_segment, sort_per_shortest_path_mlrose
from compas_slicer.sorting import align_seams
from compas_slicer.polyline_simplification import simplify_paths_rdp

from compas_slicer.fabrication import PrintOrganizer
from compas_slicer.fabrication import FDMPrinter
from compas_slicer.positioning import center_mesh_on_build_platform
from compas_slicer.fabrication import Material

######################## Logging
import logging

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = os.path.join(os.path.dirname(__file__), 'data')
INPUT_FILE = os.path.abspath(os.path.join(DATA, 'box.stl'))
OUTPUT_FILE = os.path.abspath(os.path.join(DATA, 'gcode_test.gcode'))

def main():
    ### --- Load stl
    compas_mesh = Mesh.from_stl(INPUT_FILE)

    ### --- Get machine model
    machine_model = FDMPrinter('FDM_Prusa_i3_mk2')
    machine_dimensions = machine_model.get_machine_dimensions()
    machine_model.printout_info()

    ### --- Center mesh on build platform
    compas_mesh = center_mesh_on_build_platform(compas_mesh, machine_dimensions)

    ### --- Slicer
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_cgal", layer_height=12.0)
    slicer.slice_model()
    slicer.printout_info()

    simplify_paths_rdp(slicer, threshold=0.2)
    # sort_per_shortest_path_mlrose(slicer, max_attempts=4)
    align_seams(slicer)

    ### --- Fabrication

    material_PLA = Material('PLA')
    material_PLA.set_parameter("print_speed", 70)
    material_PLA.set_parameter("z_hop", 10)
    material_PLA.printout_info()

    print_organizer = PrintOrganizer(slicer, machine_model=machine_model, material=material_PLA)
    print_organizer.generate_gcode(OUTPUT_FILE)


if __name__ == "__main__":
    main()
