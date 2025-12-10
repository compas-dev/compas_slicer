from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Point

import compas_slicer.utilities as utils
from compas_slicer.post_processing import (
    generate_brim,
    reorder_vertical_layers,
    seams_smooth,
    simplify_paths_rdp,
    sort_into_vertical_layers,
)
from compas_slicer.pre_processing import move_mesh_to_point
from compas_slicer.print_organization import (
    PlanarPrintOrganizer,
    add_safety_printpoints,
    set_blend_radius,
    set_extruder_toggle,
    set_linear_velocity_constant,
)
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.utilities import save_to_json
from compas_slicer.visualization import should_visualize, visualize_slicer

DATA_PATH = Path(__file__).parent / 'data'
OUTPUT_PATH = utils.get_output_directory(DATA_PATH)
MODEL = 'distorted_v_closed_mid_res.obj'


def main(visualize: bool = False):
    compas_mesh = Mesh.from_obj(DATA_PATH / MODEL)
    move_mesh_to_point(compas_mesh, Point(0, 0, 0))

    # Slicing
    slicer = PlanarSlicer(compas_mesh, slicer_type="cgal", layer_height=5.0)
    slicer.slice_model()

    # Sorting into vertical layers and reordering
    sort_into_vertical_layers(slicer, dist_threshold=25.0, max_paths_per_layer=25)
    reorder_vertical_layers(slicer, align_with="x_axis")

    # Post-processing
    generate_brim(slicer, layer_width=3.0, number_of_brim_offsets=5)
    simplify_paths_rdp(slicer, threshold=0.7)
    seams_smooth(slicer, smooth_distance=10)
    slicer.printout_info()
    save_to_json(slicer.to_data(), OUTPUT_PATH, 'slicer_data.json')

    # PlanarPrintOrganization
    print_organizer = PlanarPrintOrganizer(slicer)
    print_organizer.create_printpoints()

    set_extruder_toggle(print_organizer, slicer)
    add_safety_printpoints(print_organizer, z_hop=10.0)
    set_linear_velocity_constant(print_organizer, v=25.0)
    set_blend_radius(print_organizer, d_fillet=10.0)

    print_organizer.printout_info()

    printpoints_data = print_organizer.output_printpoints_dict()
    utils.save_to_json(printpoints_data, OUTPUT_PATH, 'out_printpoints.json')

    if visualize:
        visualize_slicer(slicer, compas_mesh)


if __name__ == "__main__":
    main(visualize=should_visualize())
