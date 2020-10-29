from compas_slicer.pre_processing import move_mesh_to_point
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import generate_brim
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.post_processing import seams_smooth
from compas_slicer.print_organization import PrintOrganizer
from compas_slicer.utilities import save_to_json

from compas_viewers.objectviewer import ObjectViewer
from compas.datastructures import Mesh
from compas.geometry import Point

import os
import logging

# ==============================================================================
# Logging
# ==============================================================================
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)

# ==============================================================================
# Select location of data folder and specify model to slice
# ==============================================================================

DATA = os.path.join(os.path.dirname(__file__), 'data')
MODEL = 'simple_vase.obj'


def main():
    # ==========================================================================
    # Load mesh
    # ==========================================================================
    compas_mesh = Mesh.from_obj(os.path.join(DATA, MODEL))

    # ==========================================================================
    # Move to origin
    # ==========================================================================
    move_mesh_to_point(compas_mesh, Point(0, 0, 0))

    # ==========================================================================
    # Slice the model, try out different slicers by changing the slicer_type
    # options: 'default', 'meshcut', 'cgal'
    # ==========================================================================
    slicer = PlanarSlicer(compas_mesh, slicer_type="cgal", layer_height=1.5)
    slicer.slice_model()

    # ==========================================================================
    # Generate brim
    # ==========================================================================
    # generate_brim(slicer, layer_width=3.0, number_of_brim_paths=3)

    # ==========================================================================
    # Simplify the paths by removing points with a certain threshold
    # change the threshold value to remove more or less points
    # ==========================================================================
    simplify_paths_rdp(slicer, threshold=0.3)

    # ==========================================================================
    # Smooth the seams between layers
    # change the smooth_distance value to achieve smoother, or more abrupt seams
    # ==========================================================================
    seams_smooth(slicer, smooth_distance=10)

    # ==========================================================================
    # Prints out the info of the slicer
    # ==========================================================================
    slicer.printout_info()
    
    # ==========================================================================
    # Save slicer data to JSON
    # ==========================================================================
    save_to_json(slicer.to_data(), DATA, 'slicer_data.json')

    # ==========================================================================
    # Initializes the PrintOrganizer and creates PrintPoints
    # ==========================================================================
    print_organizer = PrintOrganizer(slicer)
    print_organizer.create_printpoints(compas_mesh)

    # ==========================================================================
    # Set fabrication-related parameters
    # ==========================================================================
    print_organizer.set_extruder_toggle()
    # print_organizer.add_safety_printpoints(z_hop=20)
    print_organizer.set_linear_velocity("constant", v=25)

    # ==========================================================================
    # Converts the PrintPoints to data and saves to JSON
    # =========================================================================
    printpoints_data = print_organizer.output_printpoints_dict()
    save_to_json(printpoints_data, DATA, 'out_printpoints.json')

    # ==========================================================================
    # Initializes the compas_viewer and visualizes results
    # ==========================================================================
    viewer = ObjectViewer()
    print_organizer.visualize_on_viewer(viewer, visualize_polyline=True,
                                        visualize_printpoints=False)
    viewer.update()
    viewer.show()

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    main()
