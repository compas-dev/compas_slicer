from pathlib import Path

import numpy as np

import compas_slicer
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import generate_brim
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.print_organization import PlanarPrintOrganizer
from compas_slicer.print_organization import set_extruder_toggle
from compas_slicer.print_organization import add_safety_printpoints
from compas_slicer.print_organization.print_organization_utilities.extruder_toggle import check_assigned_extruder_toggle
from compas.datastructures import Mesh

DATA_PATH = Path(__file__).parent / "tests_data"
stl_to_test = ["distorted_v_closed_low_res.obj"]


def create_setup(filename):
    """Setting up the stage for testing."""
    compas_mesh = Mesh.from_obj(DATA_PATH / filename)
    slicer = PlanarSlicer(compas_mesh, layer_height=20)
    slicer.slice_model()
    generate_brim(slicer, layer_width=3.0, number_of_brim_offsets=3)
    simplify_paths_rdp(slicer, threshold=1.3)
    slicer.printout_info()
    print_organizer = PlanarPrintOrganizer(slicer)
    print_organizer.create_printpoints()
    return slicer, print_organizer


def test_planar_set_extruder_toggle_for_horizontal_layers():
    """Tests set_extruder_toggle on planar slicer."""

    for filename in stl_to_test:
        slicer, print_organizer = create_setup(filename)
        pp_dict = print_organizer.printpoints_dict

        set_extruder_toggle(print_organizer, slicer)
        assert check_assigned_extruder_toggle(print_organizer), (
            "Not all extruder toggles have been assigned after using 'set_extruder_toggle()'. \nFilename : "
            + str(filename)
        )

        for i, layer in enumerate(slicer.layers):
            layer_key = "layer_%d" % i
            assert not isinstance(layer, compas_slicer.geometry.VerticalLayer), (
                "You are testing vertical layers on a test for planar layers. \nFilename : " + str(filename)
            )

            # --------------- check each individual path
            for j, path in enumerate(layer.paths):
                path_key = "path_%d" % j

                # (1) --- Find how many trues and falses exist in the path
                path_extruder_toggles = [pp.extruder_toggle for pp in pp_dict[layer_key][path_key]]
                path_Trues = np.sum(np.array(path_extruder_toggles))
                path_Falses = len(path_extruder_toggles) - path_Trues

                # (2) Decide if the path should be interrupted
                path_should_be_interrupted_at_end = False

                # open path
                if not path.is_closed:
                    path_should_be_interrupted_at_end = True

                # closed path
                else:
                    if len(layer.paths) > 1:
                        if layer.is_brim:  # brim
                            if (j + 1) % layer.number_of_brim_offsets == 0:
                                path_should_be_interrupted_at_end = True
                        else:
                            path_should_be_interrupted_at_end = True

                    else:  # should only have interruption if it is the last layer of the print
                        if i == len(slicer.layers) - 1 and j == len(slicer.layers[i].paths) - 1:
                            path_should_be_interrupted_at_end = True

                # (3) Check if path has the correct number of interruptions that you decided on step (2)
                if path_should_be_interrupted_at_end:
                    assert path_Falses == 1, (
                        "On an path that should be interrupted there should be 1 extruder_toggle = "
                        "False, instead you have %d Falses.\n  The error came up on layer %d out of "
                        "total %d layers, \n path %d out of total %d paths, \n with %d printpoints. "
                        ""
                        % (
                            path_Falses,
                            i,
                            len(slicer.layers) - 1,
                            j,
                            len(slicer.layers[i].paths) - 1,
                            len(path_extruder_toggles),
                        )
                        + "\nFilename: "
                        + str(filename)
                    )
                    assert path_extruder_toggles[-1] is False, (
                        "Last printpoint of open path does not have extruder_toggle = False. \n The error is on layer "
                        "%d out of total %d layers, \n path %d of total %d paths,\n with %d printpoints. "
                        % (i, len(slicer.layers) - 1, j, len(slicer.layers[i].paths) - 1, len(path_extruder_toggles))
                        + "\nFilename: "
                        + str(filename)
                    )
                else:
                    assert path_Falses == 0, (
                        "On an path that should NOT be interrupted there should be 0 extruder_toggle "
                        "= False, instead you have %d Falses.\n  The error came up on layer %d out "
                        "of total %d layers, \n path %d out of total %d paths, \n with %d "
                        "printpoints. "
                        % (
                            path_Falses,
                            i,
                            len(slicer.layers) - 1,
                            j,
                            len(slicer.layers[i].paths) - 1,
                            len(path_extruder_toggles),
                        )
                        + "\nFilename: "
                        + str(filename)
                    )


def test_planar_add_safety_printpoints_for_horizontal_layers():
    """Tests add_safety_printpoints on planar slicer."""

    for filename in stl_to_test:
        slicer, print_organizer = create_setup(filename)
        set_extruder_toggle(print_organizer, slicer)

        pp_dict = print_organizer.printpoints_dict

        # (1) find total number of ppts and interruptions before addition of safety ppts
        initial_ppts_number = print_organizer.number_of_printpoints

        all_extruder_toggles = []
        for i, layer_key in enumerate(pp_dict):
            for j, path_key in enumerate(pp_dict[layer_key]):
                all_extruder_toggles.extend([pp.extruder_toggle for pp in pp_dict[layer_key][path_key]])
        all_Trues = np.sum(np.array(all_extruder_toggles))
        total_interruptions = len(all_extruder_toggles) - all_Trues

        # (2) add safety ppts
        add_safety_printpoints(print_organizer, z_hop=10.0)

        # (3) find resulting number of ppts
        resulting_ppts_number = print_organizer.number_of_printpoints

        assert initial_ppts_number + 2 * total_interruptions == resulting_ppts_number, (
            "Wrong number of safety points added on file : " + str(filename)
        )


def test_planar_set_linear_velocity_constant_for_horizontal_layers():
    """Tests set_linear_velocity on planar slicer, with constant value."""
    pass


def test_planar_set_blend_radius_for_horizontal_layers():
    """Tests set_blend_radius on planar slicer."""
    pass


if __name__ == "__main__":
    test_planar_set_extruder_toggle_for_horizontal_layers()
    test_planar_add_safety_printpoints_for_horizontal_layers()
