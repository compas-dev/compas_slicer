import os
from compas.datastructures import Mesh
from compas.geometry import Point

from compas_slicer.utilities import save_to_json
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import generate_brim
from compas_slicer.print_organization import PrintOrganizer
from compas_viewers.objectviewer import ObjectViewer
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.pre_processing import move_mesh_to_point

######################## Logging
import logging

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
########################

DATA = os.path.join(os.path.dirname(__file__), 'data')
MODEL = 'facade.obj'


def main():
    ### --- Load stl
    compas_mesh = Mesh.from_obj(os.path.join(DATA, MODEL))

    ### --- Move to origin
    move_mesh_to_point(compas_mesh, Point(0, 0, 0))

    ### --- Slicer
    # try out different slicers by changing the slicer_type
    # options: 'default', 'meshcut', 'cgal'
    slicer = PlanarSlicer(compas_mesh, slicer_type="default", layer_height=16.0)
    slicer.slice_model()

    ### --- Generate brim
    generate_brim(slicer, layer_width=3.0, number_of_brim_paths=3)

    ### --- Simplify the printpaths by removing points with a certain threshold
    # change the threshold value to remove more or less points
    simplify_paths_rdp(slicer, threshold=0.9)

    ### --- Prints out the info of the slicer
    slicer.printout_info()

    viewer = ObjectViewer()
    viewer.view.use_shaders = False
    slicer.visualize_on_viewer(viewer)

    save_to_json(slicer.to_data(), DATA, 'slicer_data.json')

    ### --- Fabrication - related information
    print_organizer = PrintOrganizer(slicer)
    print_organizer.create_printpoints(compas_mesh)
    print_organizer.set_extruder_toggle()
    print_organizer.add_safety_printpoints(z_hop=20)
    print_organizer.set_linear_velocity("constant", v=25)

    ### --- Save printpoints dictionary to json file
    printpoints_data = print_organizer.output_printpoints_dict()
    save_to_json(printpoints_data, DATA, 'out_printpoints.json')
    #
    # # print_organizer.visualize_on_viewer(viewer, visualize_polyline=True, visualize_printpoints=False)
    # viewer.update()
    # viewer.show()


if __name__ == "__main__":
    main()
