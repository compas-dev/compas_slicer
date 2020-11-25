import os
import compas_slicer
import numpy as np
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import generate_brim
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.post_processing import seams_smooth
from compas_slicer.print_organization import PlanarPrintOrganizer
from compas_slicer.print_organization import set_extruder_toggle
from compas_slicer.print_organization import add_safety_printpoints
from compas_slicer.print_organization import set_linear_velocity
from compas_slicer.print_organization import set_blend_radius
from compas_slicer.print_organization.print_organization_utilities.extruder_toggle import check_assigned_extruder_toggle
from compas.datastructures import Mesh
import copy

DATA = os.path.join(os.path.dirname(__file__), '..', 'data/test_geometries')
FILE = os.path.abspath(os.path.join(DATA, 'distorted_a_closed_mid_res.stl'))

# setting up the stage for the testing
compas_mesh = Mesh.from_stl(FILE)
slicer = PlanarSlicer(compas_mesh, slicer_type="default", layer_height=15)
slicer.slice_model()
generate_brim(slicer, layer_width=3.0, number_of_brim_paths=3)
simplify_paths_rdp(slicer, threshold=1.3)
seams_smooth(slicer, smooth_distance=10)
slicer.printout_info()
print_organizer = PlanarPrintOrganizer(slicer)
print_organizer.create_printpoints()


def test_planar_set_extruder_toggle_for_horizontal_layers():
    """ Tests set_extruder_toggle on planar slicer. """

    # copy to avoid altering the classes, so that all test functions can start from same setup
    print_organizer_copy = copy.deepcopy(print_organizer)
    slicer_copy = copy.deepcopy(slicer)

    set_extruder_toggle(print_organizer_copy, slicer_copy)
    assert check_assigned_extruder_toggle(
        print_organizer_copy), "Not all extruder toggles have been assigned after using 'set_extruder_toggle()'"

    pp_dict = print_organizer_copy.printpoints_dict

    # --------------- check each individual layer
    for i, layer in enumerate(slicer_copy.layers):
        layer_key = 'layer_%d' % i

        assert not isinstance(layer, compas_slicer.geometry.VerticalLayer), \
            "You are testing vertical layers on a test for planar layers"

        # (1) Find how many trues and falses exist in the layer
        layer_extruder_toggles = []
        for j, path in enumerate(layer.paths):
            path_key = 'path_%d' % j
            layer_extruder_toggles.extend([pp.extruder_toggle for pp in pp_dict[layer_key][path_key]])
            layer_Trues = np.sum(np.array(layer_extruder_toggles))
            layer_Falses = len(layer_extruder_toggles) - layer_Trues

        # (2) Decide how many interruptions it should have # TODO
        # (3) Test if layer has correct number of interruptions # TODO

        # --------------- check each individual path
        for j, path in enumerate(layer.paths):
            path_key = 'path_%d' % j

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
                    if slicer_copy.brim_toggle and i == 0:  # brim
                        if j % (slicer_copy.number_of_brim_paths + 1) == slicer_copy.number_of_brim_paths:
                            path_should_be_interrupted_at_end = True
                    else:
                        path_should_be_interrupted_at_end = True

                else:  # should only have interruption if it is the last layer of the print
                    if i == len(slicer_copy.layers) - 1 and j == len(slicer_copy.layers[i].paths) - 1:
                        path_should_be_interrupted_at_end = True

            # (3) Check if path has the correct number of interruptions that you decided on step (2)
            if path_should_be_interrupted_at_end:
                assert path_Falses == 1, "On an path that should be interrupted there should be 1 extruder_toggle = " \
                                         "False, instead you have %d Falses.\n  The error came up on layer %d out of " \
                                         "total %d layers, \n path %d out of total %d paths, \n with %d printpoints. " \
                                         "" % (path_Falses, i, len(slicer_copy.layers) - 1, j,
                                               len(slicer_copy.layers[i].paths) - 1,
                                               len(path_extruder_toggles))
                assert path_extruder_toggles[-1] is False, "Last printpoint of open path does not have " \
                                                           "extruder_toggle = False. \n The error is on layer %d " \
                                                           "out of total %d layers, \n path %d of total %d paths, " \
                                                           "\n with %d printpoints. " % (
                                                           i, len(slicer_copy.layers) - 1, j,
                                                           len(slicer_copy.layers[i].paths) - 1,
                                                           len(path_extruder_toggles))
            else:
                assert path_Falses == 0, "On an path that should NOT be interrupted there should be 0 extruder_toggle " \
                                         "= False, instead you have %d Falses.\n  The error came up on layer %d out " \
                                         "of total %d layers, \n path %d out of total %d paths, \n with %d " \
                                         "printpoints. " % (path_Falses, i, len(slicer_copy.layers) - 1, j,
                                                            len(slicer_copy.layers[i].paths) - 1,
                                                            len(path_extruder_toggles))


def test_planar_add_safety_printpoints_for_horizontal_layers():
    """ Tests add_safety_printpoints on planar slicer. """

    # copy to avoid altering the classes, so that all test functions can start from same setup
    print_organizer_copy = copy.deepcopy(print_organizer)
    slicer_copy = copy.deepcopy(slicer)
    set_extruder_toggle(print_organizer_copy, slicer_copy)

    pp_dict = print_organizer_copy.printpoints_dict

    # (1) find total number of ppts and interruptions before addition of safety ppts
    initial_ppts_number = print_organizer_copy.total_number_of_points

    all_extruder_toggles = []
    for i, layer_key in enumerate(pp_dict):
        for j, path_key in enumerate(pp_dict[layer_key]):
            all_extruder_toggles.extend([pp.extruder_toggle for pp in pp_dict[layer_key][path_key]])
    all_Trues = np.sum(np.array(all_extruder_toggles))
    total_interruptions = len(all_extruder_toggles) - all_Trues

    # (2) add safety ppts
    add_safety_printpoints(print_organizer_copy, z_hop=10.0)

    # (3) find resulting number of ppts
    resulting_ppts_number = print_organizer_copy.total_number_of_points

    assert initial_ppts_number + 2 * total_interruptions == resulting_ppts_number, "OFF"


def test_planar_set_linear_velocity_constant_for_horizontal_layers():
    """ Tests set_linear_velocity on planar slicer, with constant value. """
    #
    # # copy to avoid altering the classes, so that all test functions can start from same setup
    # print_organizer_copy = copy.deepcopy(print_organizer)
    # slicer_copy = copy.deepcopy(slicer)
    #
    # set_linear_velocity(print_organizer_copy, "constant", v=25.0)
    pass
    # TODO check results


def test_planar_set_blend_radius_for_horizontal_layers():
    """ Tests set_blend_radius on planar slicer. """
    #
    # # copy to avoid altering the classes, so that all test functions can start from same setup
    # print_organizer_copy = copy.deepcopy(print_organizer)
    # slicer_copy = copy.deepcopy(slicer)
    #
    # set_blend_radius(print_organizer_copy, d_fillet=10.0)
    pass
    # TODO check results
