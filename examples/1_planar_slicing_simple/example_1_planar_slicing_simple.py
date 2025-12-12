import time
from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Point

import compas_slicer.utilities as utils
from compas_slicer.post_processing import generate_brim, generate_raft, seams_align, seams_smooth, simplify_paths_rdp
from compas_slicer.pre_processing import move_mesh_to_point
from compas_slicer.print_organization import (
    PlanarPrintOrganizer,
    add_safety_printpoints,
    set_extruder_toggle,
    set_linear_velocity_constant,
)
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.utilities import save_to_json
from compas_slicer.visualization import should_visualize, visualize_slicer

DATA_PATH = Path(__file__).parent / 'data'
OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
MODEL = 'simple_vase_open_low_res.obj'


def main(visualize: bool = False):
    start_time = time.time()

    # Load mesh
    compas_mesh = Mesh.from_obj(DATA_PATH / MODEL)

    # Move to origin
    move_mesh_to_point(compas_mesh, Point(0, 0, 0))

    # Slicing
    slicer = PlanarSlicer(compas_mesh, layer_height=1.5)
    slicer.slice_model()

    seams_align(slicer, "next_path")

    # Generate brim / raft
    # NOTE: Typically you would want to use either a brim OR a raft,
    # however, in this example both are used to explain the functionality
    generate_brim(slicer, layer_width=3.0, number_of_brim_offsets=4)
    generate_raft(slicer,
                  raft_offset=20,
                  distance_between_paths=5,
                  direction="xy_diagonal",
                  raft_layers=1)

    # Simplify the paths by removing points with a certain threshold
    simplify_paths_rdp(slicer, threshold=0.6)

    # Smooth the seams between layers
    seams_smooth(slicer, smooth_distance=10)

    slicer.printout_info()
    save_to_json(slicer.to_data(), OUTPUT_PATH, 'slicer_data.json')

    # Print organization
    print_organizer = PlanarPrintOrganizer(slicer)
    print_organizer.create_printpoints(generate_mesh_normals=False)

    # Set fabrication-related parameters
    set_extruder_toggle(print_organizer, slicer)
    add_safety_printpoints(print_organizer, z_hop=10.0)
    set_linear_velocity_constant(print_organizer, v=25.0)

    print_organizer.printout_info()

    printpoints_data = print_organizer.output_printpoints_dict()
    utils.save_to_json(printpoints_data, OUTPUT_PATH, 'out_printpoints.json')

    printpoints_data = print_organizer.output_nested_printpoints_dict()
    utils.save_to_json(printpoints_data, OUTPUT_PATH, 'out_printpoints_nested.json')

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")

    if visualize:
        visualize_slicer(slicer, compas_mesh)


if __name__ == "__main__":
    main(visualize=should_visualize())
