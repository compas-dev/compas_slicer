.. _compas_slicer_example_6:

************************************
Transferring attributes to PrintPoints
************************************

Often in 3D printing we need to transfer information from the mesh that is being sliced to the PrintPoints that
are used in the fabrication process. We might want, for example, to print paths that are generated from different parts of
the geometry using different parameters. This is enabled by the *transfer_mesh_attributes_to_printpoints()* function, as
shown in the example below. During the slicing process each printpoint is projected to the closest mesh face.
It takes directly all the face attributes, and it takes the averaged vertex attributes of the face vertices using
barycentric coordinates.

.. figure:: figures/06_attributes.png
    :figclass: figure
    :class: figure-img img-fluid

    *PrintPoints with visualization of the attribute: overhang angle of the underlying mesh.*


.. code-block:: python

    import logging
    import os
    from compas.geometry import Point, Vector, distance_point_plane, normalize_vector
    from compas.datastructures import Mesh
    import compas_slicer.utilities as slicer_utils
    from compas_slicer.post_processing import simplify_paths_rdp_igl
    from compas_slicer.slicers import PlanarSlicer
    import compas_slicer.utilities.utils as utils
    from compas_slicer.utilities.attributes_transfer import transfer_mesh_attributes_to_printpoints
    from compas_slicer.print_organization import PlanarPrintOrganizer
    import numpy as np

    logger = logging.getLogger('logger')
    logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)

    DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
    OUTPUT_PATH = slicer_utils.get_output_directory(DATA_PATH)
    MODEL = 'distorted_v_closed_low_res.obj'

    if __name__ == '__main__':
        # load mesh
        mesh = Mesh.from_obj(os.path.join(DATA_PATH, MODEL))

        # --------------- Add attributes to mesh
        # Face attributes can be anything (ex. float, bool, array, text ...)
        # Vertex attributes can only be entities that can be meaningfully multiplied with a float (ex. float, np.array ...)

        # overhand attribute - Scalar value (per face)
        mesh.update_default_face_attributes({'overhang': 0.0})
        for f_key, data in mesh.faces(data=True):
            face_normal = mesh.face_normal(f_key, unitized=True)
            data['overhang'] = Vector(0.0, 0.0, 1.0).dot(face_normal)

        # face looking towards the positive y axis - Boolean value (per face)
        mesh.update_default_face_attributes({'positive_y_axis': False})
        for f_key, data in mesh.faces(data=True):
            face_normal = mesh.face_normal(f_key, unitized=True)
            is_positive_y = Vector(0.0, 1.0, 0.0).dot(face_normal) > 0  # boolean value
            data['positive_y_axis'] = is_positive_y

        # distance from plane - Scalar value (per vertex)
        mesh.update_default_vertex_attributes({'dist_from_plane': 0.0})
        plane = (Point(0.0, 0.0, -30.0), Vector(0.0, 0.5, 0.5))
        for v_key, data in mesh.vertices(data=True):
            v_coord = mesh.vertex_coordinates(v_key, axes='xyz')
            data['dist_from_plane'] = distance_point_plane(v_coord, plane)

        # direction towards point - Vector value (per vertex)
        mesh.update_default_vertex_attributes({'direction_to_pt': 0.0})
        pt = Point(4.0, 1.0, 0.0)
        for v_key, data in mesh.vertices(data=True):
            v_coord = mesh.vertex_coordinates(v_key, axes='xyz')
            data['direction_to_pt'] = np.array(normalize_vector(Vector.from_start_end(v_coord, pt)))

        # --------------- Slice mesh
        slicer = PlanarSlicer(mesh, slicer_type="default", layer_height=5.0)
        slicer.slice_model()
        simplify_paths_rdp_igl(slicer, threshold=1.0)
        slicer_utils.save_to_json(slicer.to_data(), OUTPUT_PATH, 'slicer_data.json')

        # --------------- Create printpoints
        print_organizer = PlanarPrintOrganizer(slicer)
        print_organizer.create_printpoints()

        # --------------- Transfer mesh attributes to printpoints
        transfer_mesh_attributes_to_printpoints(mesh, print_organizer.printpoints_dict)

        # --------------- Save printpoints to json (only json-serializable attributes are saved)
        printpoints_data = print_organizer.output_printpoints_dict()
        utils.save_to_json(printpoints_data, OUTPUT_PATH, 'out_printpoints.json')

        # --------------- Print the info to see the attributes of the printpoints (you can also visualize them on gh)
        print_organizer.printout_info()

        # --------------- Save printpoints attributes for visualization
        overhangs_list = print_organizer.get_printpoints_attribute(attr_name='overhang')
        positive_y_axis_list = print_organizer.get_printpoints_attribute(attr_name='positive_y_axis')
        dist_from_plane_list = print_organizer.get_printpoints_attribute(attr_name='dist_from_plane')
        direction_to_pt_list = print_organizer.get_printpoints_attribute(attr_name='direction_to_pt')

        utils.save_to_json(overhangs_list, OUTPUT_PATH, 'overhangs_list.json')
        utils.save_to_json(positive_y_axis_list, OUTPUT_PATH, 'positive_y_axis_list.json')
        utils.save_to_json(dist_from_plane_list, OUTPUT_PATH, 'dist_from_plane_list.json')
        utils.save_to_json(utils.point_list_to_dict(direction_to_pt_list), OUTPUT_PATH, 'direction_to_pt_list.json')