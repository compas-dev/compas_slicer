import os
from compas.datastructures import Mesh
from compas.geometry import Point, Frame

from compas_slicer.utilities import save_to_json
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import generate_brim
from compas_slicer.post_processing import spiralize_contours
from compas_slicer.post_processing import seams_align
from compas_slicer.post_processing import seams_smooth, unify_paths_orientation
from compas_slicer.print_organization import PrintOrganizer
from compas_viewers.objectviewer import ObjectViewer
from compas_slicer.post_processing import move_mesh_to_point, simplify_paths_rdp
import time

######################## Logging
import logging
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = os.path.join(os.path.dirname(__file__), 'data')
MODEL = 'simple_vase.obj'

start_time = time.time()


def main():
    ### --- Load stl
    compas_mesh = Mesh.from_obj(os.path.join(DATA, MODEL))

    ### --- Move to origin
    move_mesh_to_point(compas_mesh, Point(0, 0, 0))

    ### --- Slicer
    # try out different slicers by changing the slicer_type
    # options: 'planar', 'planar_meshcut', 'planar_cgal'
    slicer = PlanarSlicer(compas_mesh, slicer_type="default", layer_height=1.5)
    slicer.slice_model()

    ### --- Generate brim
    generate_brim(slicer, layer_width=3.0, number_of_brim_paths=3)

    ### --- Simplify the printpaths by removing points with a certain threshold
    # change the threshold value to remove more or less points
    simplify_paths_rdp(slicer, threshold=1.5)

    ### --- Smooth the seams between layers
    # change the smooth_distance value to achieve smoother, or more abrupt seams
    seams_smooth(slicer, smooth_distance=10)

    # WIP
    # spiralize_contours(slicer)

    ### --- Prints out the info of the slicer
    slicer.printout_info()

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")

    viewer = ObjectViewer()
    viewer.view.use_shaders = False
    slicer.visualize_on_viewer(viewer)

    save_to_json(slicer.to_data(), DATA, 'slicer_data.json')

    ### --- Fabrication - related information
    # options extruder_toggle_type: always_on, always_off, off_when_travel
    print_organizer = PrintOrganizer(slicer)
    print_organizer.create_printpoints(compas_mesh)
    print_organizer.set_extruder_toggle(extruder_toggle_type="always_on")
    print_organizer.add_safety_printpoints(z_hop=20)
    print_organizer.set_linear_velocity("constant", v=25)

    ### --- Save printpoints dictionary to json file
    printpoints_data = print_organizer.output_printpoints_dict()
    save_to_json(printpoints_data, DATA, 'out_printpoints.json')

    # print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)
    viewer.update()
    viewer.show()


if __name__ == "__main__":
    main()
