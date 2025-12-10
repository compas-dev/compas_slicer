.. _compas_slicer_example_1:

****************************
Simple planar slicing
****************************

A general introduction of the concepts organization of compas_slicer can be found in the :ref:`introduction tutorial <compas_slicer_tutorial_1_introduction>`.

This example describes the planar slicing process for a simple shape, consisting
out of a shape with a single contour (also known as a 'vase'). Its files can be found in the folder `/examples/1_planar_slicing_simple/`

Imports and initialization
==========================

The first step is to import the required functions:

.. code-block:: python

    import time
    from pathlib import Path

    from loguru import logger

    import compas_slicer.utilities as utils
    from compas_slicer.pre_processing import move_mesh_to_point
    from compas_slicer.slicers import PlanarSlicer
    from compas_slicer.post_processing import generate_brim
    from compas_slicer.post_processing import generate_raft
    from compas_slicer.post_processing import simplify_paths_rdp
    from compas_slicer.post_processing import seams_smooth
    from compas_slicer.post_processing import seams_align
    from compas_slicer.print_organization import PlanarPrintOrganizer
    from compas_slicer.print_organization import set_extruder_toggle
    from compas_slicer.print_organization import add_safety_printpoints
    from compas_slicer.print_organization import set_linear_velocity_constant
    from compas_slicer.print_organization import set_blend_radius
    from compas_slicer.utilities import save_to_json

    from compas.datastructures import Mesh
    from compas.geometry import Point

Loguru is used for logging messages from compas_slicer. It's already configured by default.

Next we point to the data folder. Compas_slicer assumed there is a folder named ``data``
where it looks for the model to slice. The model to slice can be of type ``.stl`` or ``.obj``.
In the data folder compas_slicer will create a folder called ``output``, where all the intermediate and final outputs
of the slicing process will be saved. Therefore, we run the command ``get_output_directory(DATA)``, which
checks if the ``output`` folder exists and if not, it creates it.

.. code-block:: python

    DATA_PATH = Path(__file__).parent / 'data'
    OUTPUT_DIR = utils.get_output_directory(DATA_PATH)  # creates 'output' folder if it doesn't already exist
    MODEL = 'simple_vase_open_low_res.obj'


Slicing process
===============

In the next step we use the Compas function ``Mesh.from_obj`` to load our ``.obj`` 
file. We then move it to the origin, but this can be any specified point, such as 
a point on your print bed.

.. code-block:: python

    compas_mesh = Mesh.from_obj(DATA_PATH / MODEL)
    move_mesh_to_point(compas_mesh, Point(0, 0, 0))

Next, we initialize the :class:`PlanarSlicer` to initialize the slicing process. You need to specify the layer height.
Slicing uses CGAL for fast mesh-plane intersection.

.. code-block:: python

    slicer = PlanarSlicer(compas_mesh, layer_height=1.5)
    slicer.slice_model()


We also align the seams so that the start of each path is as close as possible to the start of the previous path

.. code-block:: python

    seams_align(slicer, "next_path")


After the model has been sliced, several post processing operations can be executed.
One useful functionality is ``generate_brim``, which generates a number of layers
that are offset from the bottom layer, to improve adhesion to the build plate 
(see image). Also, a raft can be generated using the ``generate_raft`` command.

.. figure:: figures/01_brim.jpg
    :figclass: figure
    :class: figure-img img-fluid

    *Left: Without brim. Right: With brim*

.. code-block:: python

    generate_brim(slicer, layer_width=3.0, number_of_brim_offsets=4)
    generate_raft(slicer,
                  raft_offset=20,
                  distance_between_paths=5,
                  direction="xy_diagonal",
                  raft_layers=1)

Depending on the amount of faces that your input mesh has, a very large amount of 
points can be generated. ``simplify_paths_rdp_igl`` removes points
that do not have a high impact on the final shape of the polyline. Increase the
threshold value to remove more points, decrease it to remove less. For more 
information on how the algorithm works see: `Ramer–Douglas–Peucker algorithm <https://en.wikipedia.org/wiki/Ramer-Douglas-Peucker_algorithm>`_

.. code-block:: python

    simplify_paths_rdp(slicer, threshold=0.6)

Currently the 'seam' between different layers of our shape is a 'hard seam',
the printer would move up almost vertically to move to the next layer. 
To make the seam more 'smooth', and less visible we can use the 
``seams_smooth`` function. This function simply removes points within the specified distance to enable
a smoother motion from one layer to the next.

.. code-block:: python

    seams_smooth(slicer, smooth_distance=10)

To get information on the current state of the slicing process we can print out 
information from the slicing process. 

.. code-block:: python

    slicer.printout_info()

Since we are now done with operations involving the :class:`PlanarSlicer` class,
we can save the slicing result to JSON. In the next steps we will use the 
:class:`PlanarPrintOrganizer` class to organize our print for fabrication.

.. code-block:: python

    save_to_json(slicer.to_data(), OUTPUT_DIR, 'slicer_data.json')


Print organization
==================

In the next steps of the process we will use the :class:`PlanarPrintOrganizer` to
make our slicing result ready for fabrication. First, we initialize the 
:class:`PlanarPrintOrganizer` and create :class:`PrintPoints`. The difference between
:class:`PrintPoints` and the ``compas.geometry.Points`` we were using in the
previous step is that the :class:`PrintPoints` have all the necessary additional information that is
needed for the fabrication process.

.. code-block:: python

    print_organizer = PlanarPrintOrganizer(slicer)
    print_organizer.create_printpoints(compas_mesh)

We can add these additional functionalities to the printpoints by calling 
different functions. 

* `set_extruder_toggle`: Adds a boolean ``extruder_toggle`` to the PrintPoints. ``True`` means the extruder should be on (printing), whereas ``False`` means the extruder should be off (when traveling between paths).
* `add_safety_printpoints`: This function adds a 'safety point' (also known as 'z-hop') before and after print paths, to make sure the extruder does not collide with the print. This is recommended for prints consisting out of multiple contours.
* `set_linear_velocity`: Sets the linear velocity (printing speed) for the print. 

.. code-block:: python

    set_extruder_toggle(print_organizer, slicer)
    add_safety_printpoints(print_organizer, z_hop=10.0)
    set_linear_velocity_constant(print_organizer, v=25.0)

Again we can print out the information about the print_organizer.

.. code-block:: python

    print_organizer.printout_info()

After adding all of the fabrication-related parameters we will convert the Printpoints into a dictionary of data
and then export it to a ``.JSON`` file.

.. code-block:: python

    printpoints_data = print_organizer.output_printpoints_dict()
    save_to_json(printpoints_data, DATA, 'out_printpoints.json')


Once the slicing process is finished, you can use the compas_slicer grasshopper components to visualize the results,
described in the :ref:`grasshopper tutorial <compas_slicer_tutorial_2>`.

To view the results of the slicing process, open the `planar_slicing_master.gh` file in `examples/1_planar_slicing_simple`. This loads the
json and txt files that have been produced and displays them as Rhino-Grasshopper geometry. You will only be able to visualize
the results after you have run the python file that generates them.

Final script
============

The completed final script can be found below:

.. code-block:: python

    import time
    from pathlib import Path

    from loguru import logger

    import compas_slicer.utilities as utils
    from compas_slicer.pre_processing import move_mesh_to_point
    from compas_slicer.slicers import PlanarSlicer
    from compas_slicer.post_processing import generate_brim
    from compas_slicer.post_processing import generate_raft
    from compas_slicer.post_processing import simplify_paths_rdp
    from compas_slicer.post_processing import seams_smooth
    from compas_slicer.post_processing import seams_align
    from compas_slicer.print_organization import PlanarPrintOrganizer
    from compas_slicer.print_organization import set_extruder_toggle
    from compas_slicer.print_organization import add_safety_printpoints
    from compas_slicer.print_organization import set_linear_velocity_constant
    from compas_slicer.print_organization import set_blend_radius
    from compas_slicer.utilities import save_to_json

    from compas.datastructures import Mesh
    from compas.geometry import Point

    # ==============================================================================
    # Select location of data folder and specify model to slice
    # ==============================================================================
    DATA_PATH = Path(__file__).parent / 'data'
    OUTPUT_DIR = utils.get_output_directory(DATA_PATH)  # creates 'output' folder if it doesn't already exist
    MODEL = 'simple_vase_open_low_res.obj'


    def main():
        start_time = time.time()

        # ==========================================================================
        # Load mesh
        # ==========================================================================
        compas_mesh = Mesh.from_obj(DATA_PATH / MODEL)

        # ==========================================================================
        # Move to origin
        # ==========================================================================
        move_mesh_to_point(compas_mesh, Point(0, 0, 0))

        # ==========================================================================
        # Slicing
        # ==========================================================================
        slicer = PlanarSlicer(compas_mesh, layer_height=1.5)
        slicer.slice_model()

        seams_align(slicer, "next_path")

        # ==========================================================================
        # Generate brim / raft
        # ==========================================================================
        # NOTE: Typically you would want to use either a brim OR a raft,
        # however, in this example both are used to explain the functionality
        generate_brim(slicer, layer_width=3.0, number_of_brim_offsets=4)
        generate_raft(slicer,
                      raft_offset=20,
                      distance_between_paths=5,
                      direction="xy_diagonal",
                      raft_layers=1)

        # ==========================================================================
        # Simplify the paths by removing points with a certain threshold
        # change the threshold value to remove more or less points
        # ==========================================================================
        simplify_paths_rdp(slicer, threshold=0.6)

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
        save_to_json(slicer.to_data(), OUTPUT_DIR, 'slicer_data.json')

        # ==========================================================================
        # Initializes the PlanarPrintOrganizer and creates PrintPoints
        # ==========================================================================
        print_organizer = PlanarPrintOrganizer(slicer)
        print_organizer.create_printpoints(generate_mesh_normals=False)

        # ==========================================================================
        # Set fabrication-related parameters
        # ==========================================================================
        set_extruder_toggle(print_organizer, slicer)
        add_safety_printpoints(print_organizer, z_hop=10.0)
        set_linear_velocity_constant(print_organizer, v=25.0)

        # ==========================================================================
        # Prints out the info of the PrintOrganizer
        # ==========================================================================
        print_organizer.printout_info()

        # ==========================================================================
        # Converts the PrintPoints to data and saves to JSON
        # =========================================================================
        printpoints_data = print_organizer.output_printpoints_dict()
        utils.save_to_json(printpoints_data, OUTPUT_DIR, 'out_printpoints.json')

        printpoints_data = print_organizer.output_nested_printpoints_dict()
        utils.save_to_json(printpoints_data, OUTPUT_DIR, 'out_printpoints_nested.json')

        end_time = time.time()
        print("Total elapsed time", round(end_time - start_time, 2), "seconds")


    if __name__ == "__main__":
        main()