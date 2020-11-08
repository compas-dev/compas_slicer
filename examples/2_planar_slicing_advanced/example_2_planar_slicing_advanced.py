import os
from compas.datastructures import Mesh
from compas.geometry import Point
import time
import compas_slicer.utilities as utils
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import generate_brim
from compas_slicer.print_organization import PlanarPrintOrganizer
from compas_viewers.objectviewer import ObjectViewer
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.pre_processing import move_mesh_to_point
from compas_slicer.print_organization import set_extruder_toggle, add_safety_printpoints, set_linear_velocity

######################## Logging
import logging

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
########################

DATA = os.path.join(os.path.dirname(__file__), 'data')
OUTPUT_DIR = utils.get_output_directory(DATA)  # creates 'output' folder if it doesn'weight already exist
MODEL = 'facade.obj'


def main():
    start_time = time.time()

    ### --- Load stl
    compas_mesh = Mesh.from_obj(os.path.join(DATA, MODEL))

    ### --- Move to origin
    move_mesh_to_point(compas_mesh, Point(0, 0, 0))

    ### --- Slicer
    # try out different slicers by changing the slicer_type
    # options: 'default', 'meshcut', 'cgal'
    slicer = PlanarSlicer(compas_mesh, slicer_type="default", layer_height=1.5)
    slicer.slice_model()

    ### --- Generate brim
    generate_brim(slicer, layer_width=3.0, number_of_brim_paths=3)

    ### --- Simplify the paths by removing points with a certain threshold
    # change the threshold value to remove more or less points
    simplify_paths_rdp(slicer, threshold=0.9)

    ### --- Prints out the info of the slicer
    slicer.printout_info()

    viewer = ObjectViewer()
    viewer.view.use_shaders = False
    slicer.visualize_on_viewer(viewer)

    utils.save_to_json(slicer.to_data(), OUTPUT_DIR, 'slicer_data.json')

    ### --- Fabrication - related information
    print_organizer = PlanarPrintOrganizer(slicer)
    print_organizer.create_printpoints()

    set_extruder_toggle(print_organizer, slicer)
    add_safety_printpoints(print_organizer, z_hop=20.0)
    set_linear_velocity(print_organizer, "constant", v=25.0)

    ### --- Save printpoints dictionary to json file
    printpoints_data = print_organizer.output_printpoints_dict()
    utils.save_to_json(printpoints_data, OUTPUT_DIR, 'out_printpoints.json')

    # # print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)
    viewer.update()
    viewer.show()

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")


if __name__ == "__main__":
    main()
