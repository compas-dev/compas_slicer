import time
import os
import logging

import compas_slicer.utilities as utils
from compas_slicer.pre_processing import move_mesh_to_point
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import generate_brim
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.post_processing import sort_into_vertical_layers
from compas_slicer.post_processing import reorder_vertical_layers
from compas_slicer.post_processing import seams_smooth
from compas_slicer.print_organization import PlanarPrintOrganizer
from compas_slicer.print_organization import set_extruder_toggle
from compas_slicer.print_organization import add_safety_printpoints
from compas_slicer.print_organization import set_linear_velocity_constant
from compas_slicer.print_organization import set_blend_radius
from compas_slicer.utilities import save_to_json
from compas_viewers.objectviewer import ObjectViewer

from compas.datastructures import Mesh
from compas.geometry import Point

# ==============================================================================
# Logging
# ==============================================================================
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)

# ==============================================================================
# Select location of data folder and specify model to slice
# ==============================================================================
DATA = os.path.join(os.path.dirname(__file__), 'data')
OUTPUT_DIR = utils.get_output_directory(DATA)  # creates 'output' folder if it doesn't already exist
MODEL = 'distorted_v_closed_mid_res.obj'


def main():
    compas_mesh = Mesh.from_obj(os.path.join(DATA, MODEL))
    move_mesh_to_point(compas_mesh, Point(0, 0, 0))

    # Slicing
    slicer = PlanarSlicer(compas_mesh, slicer_type="cgal", layer_height=5.0)
    slicer.slice_model()

    # Sorting into vertical layers and reordering
    sort_into_vertical_layers(slicer, max_paths_per_layer=10)
    reorder_vertical_layers(slicer, align_with="x_axis")

    # Post-processing
    generate_brim(slicer, layer_width=3.0, number_of_brim_offsets=5)
    simplify_paths_rdp(slicer, threshold=0.7)
    seams_smooth(slicer, smooth_distance=10)
    slicer.printout_info()
    save_to_json(slicer.to_data(), OUTPUT_DIR, 'slicer_data.json')

    # PlanarPrintOrganization
    print_organizer = PlanarPrintOrganizer(slicer)
    print_organizer.create_printpoints()

    set_extruder_toggle(print_organizer, slicer)
    add_safety_printpoints(print_organizer, z_hop=10.0)
    set_linear_velocity_constant(print_organizer, v=25.0)
    set_blend_radius(print_organizer, d_fillet=10.0)

    print_organizer.printout_info()

    printpoints_data = print_organizer.output_printpoints_dict()
    utils.save_to_json(printpoints_data, OUTPUT_DIR, 'out_printpoints.json')

    # ==========================================================================
    # Initializes the compas_viewer and visualizes results
    # ==========================================================================
    viewer = ObjectViewer()
    print_organizer.visualize_on_viewer(viewer, visualize_polyline=True,
                                        visualize_printpoints=False)
    viewer.view.use_shaders = False
    viewer.update()
    viewer.show()


if __name__ == "__main__":
    main()
