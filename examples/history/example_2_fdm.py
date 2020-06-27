'''
Example code structures for compas_slicer

author :  Ioanna Mitropoulou
email: mitropoulou@arch.ethz.ch
date: 20.04.2020

===================
STRUCTURE 2
===================

compas_slicer.input
    mesh / brep - open / closed
    sanitize input (ex. in case of holes: close)    

compas_slicer.position
    position and orient input shape within reach
    orient shape to reduce need for support 
    segmentation? - design seams

compas_slicer.supports
    supports : identify and visualize big overhangs 

compas_slicer.slicing
    Slicing
        slice planar layers with regular height
        slice planar layers with adaptive height
        slice curved layers 

    infill generation

    align seams
    randomize seams
    orient curves 
    cull small curves 
    solve self intersections 
    find issues - Satinize the curves


compas_slicer.sorting
    sort per layer - shortest path at the same z height
    sort per segment - less interruptions 
    sort by longest path


compas_slicer.sampling
    Descrete polylines: 
        cull points within a threshold (to reduce too many input curves)
        cull points based on curvature - adaptive polygon simplification

-gcode

compas_slicer.commands

    generate commands
    save commands 
    import commands
    
    Need to agree on a universal Json template for commands 
    Ex:
    Command
    (Frame: ... , End effector parameters: ..., Waiting time: ..., Robot configuration: ..., Blend radius: ..., 
    velocity: ..., acceleration: ... )

    Then each project can only fill in the parameters they need 


compas_slicer.fabrication_data
    generate_ur_script(commands) 
    save_ur_script(script, filename)

    generate_rapid(commands) 
    save_rapid

compas_slicer.send_commands
    UR direct communication
    Rapid ?... 


compas_slicer.non_planar_printing
    generate_print_orientation 
    collision check
    orientation smoothing 
    velocity calculation

'''


def generate_commands():

    mesh = import_mesh(filename, type = open/closed)

    mesh = compas_am.position_geometry(mesh, machine_bounds)

    mesh = compas_am.orient_geometry(mesh, type = "minimize_overhangs")

    slices = compas_am.slice_mesh(mesh, type = "regular", z_height = 1.0, min_curve_length = 10.0, orient = True, align_seams = True)

    slices = compas_am.sort_slices(slices, type = "shortest_path")

    slices = compas_am.adaptive_subsampling(slices, thershold = 2.23 )

    commands = compas_am.generate_commands(slices, type = "planar printing" / "non-planar printing")

    compas_am.save_commands(commands , Json_filename)


def generate_robot_script():

    commands = compas_am.load_commands(commands , Json_filename)

    script = compas_am.generate_UR_script()


def send_robot_script():

    script = compas_am.load_script(filename)

    send_robot_script(script)










