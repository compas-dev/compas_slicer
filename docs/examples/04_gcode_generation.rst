.. _compas_slicer_example_4:

************************************
Gcode generation
************************************

While compas slicer has been mostly developed for robotic printing, we can also export the gcode of the generated paths
to materialize them in a typical desktop 3D printer. The gcode generation is still at a basic level and is a work in progress.
The following file can be found in `/examples/4_gcode_generation/`. The gcode file is placed in the `/output/` folder.


.. code-block:: python

    import os
    import logging
    import compas_slicer.utilities as utils
    from compas_slicer.pre_processing import move_mesh_to_point
    from compas_slicer.slicers import PlanarSlicer
    from compas_slicer.post_processing import generate_brim
    from compas_slicer.post_processing import simplify_paths_rdp_igl
    from compas_slicer.post_processing import seams_smooth
    from compas_slicer.print_organization import PlanarPrintOrganizer
    from compas_slicer.print_organization import set_extruder_toggle
    from compas_slicer.utilities import save_to_json
    from compas_slicer.parameters import get_param

    from compas.datastructures import Mesh
    from compas.geometry import Point

    logger = logging.getLogger('logger')
    logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)

    DATA = os.path.join(os.path.dirname(__file__), 'data')
    OUTPUT_DIR = utils.get_output_directory(DATA)  # creates 'output' folder if it doesn't already exist
    MODEL = 'simple_vase_open_low_res.obj'


    def main():

        compas_mesh = Mesh.from_obj(os.path.join(DATA, MODEL))
        delta = get_param({}, key='delta', defaults_type='gcode')  # boolean for delta printers
        print_volume_x = get_param({}, key='print_volume_x', defaults_type='gcode')  # in mm
        print_volume_y = get_param({}, key='print_volume_y', defaults_type='gcode')  # in mm
        if delta:
            move_mesh_to_point(compas_mesh, Point(0, 0, 0))
        else:
            move_mesh_to_point(compas_mesh, Point(print_volume_x/2, print_volume_y/2, 0))

        # ----- slicing
        slicer = PlanarSlicer(compas_mesh, slicer_type="cgal", layer_height=4.5)
        slicer.slice_model()
        generate_brim(slicer, layer_width=3.0, number_of_brim_offsets=4)
        simplify_paths_rdp_igl(slicer, threshold=0.6)
        seams_smooth(slicer, smooth_distance=10)
        slicer.printout_info()
        save_to_json(slicer.to_data(), OUTPUT_DIR, 'slicer_data.json')

        # ----- print organization
        print_organizer = PlanarPrintOrganizer(slicer)
        print_organizer.create_printpoints()
        # Set fabrication-related parameters
        set_extruder_toggle(print_organizer, slicer)
        print_organizer.printout_info()

        # create and output gcode
        gcode_parameters = {}  # leave all to default
        gcode_text = print_organizer.output_gcode(gcode_parameters)
        utils.save_to_text_file(gcode_text, OUTPUT_DIR, 'my_gcode.gcode')


    if __name__ == "__main__":
        main()
