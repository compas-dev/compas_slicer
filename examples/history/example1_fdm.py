'''
Example code structures for compas_slicer

author : Joris Burger
email: burger@arch.ethz.ch
date: 20.04.2020

===================
EXAMPLE STRUCTURE 1
===================

compas_slicer.geometry
    compas_slicer.geometry.mesh
    --- contour_geometry(mesh, layer_height)
    --- get_bounding_box(mesh)
    --- get_mesh_normals(mesh)
    --- generate_supports(mesh)

    compas_slicer.geometry.polyline
    --- divide_into_points(polyline, point_distance) 
    --- sort_by_z(polyline_list)
    --- shortest_path(polyline_list)
    --- generate_infill(polyline, infill_type, infill_percentage)

    compas_slicer.geometry.point
    --- sort_per_layer(point_list)

compas_slicer.fabrication
    compas_slicer.fabrication.fdm
    --- generate_gcode(point_list, many parameters)

    compas_slicer.fabrication.rob_fdm
    --- generate_ur_script(point_list, many parameters)
    --- generate_rapid(point_list, many parameters)
    --- etc.
'''

def __init__(self, layer_height, distance_between_points, fix_self_intersections, intersection_threshold, smooth_curves, smoothing_factor):

def main_robfdm(input_geometry):
    # STEP 1: contour geometry
    point_list = contour_geometry(input_geometry)

    # STEP 2: generate ur_script
    script = generate(ur_script)

    return script

def contour_geometry(self, input_geometry):

    """ Creates curves and points from an input geometry by generating contours.
    """
    
    # 1. Gets minimun and maximum z value
    min_z, max_z = get_bounding_box(input_geometry)

    # 2. Create contour curves
    if input_geometry.Type == Mesh:
        contour_curves = contour_curve_mesh(input_geometry)
    elif input_geometry.Type == Brep:
        contour_curves = contour_curve_brep(input_geometry)

    # 3. Removes too short (invalid) curves
    contour_curves, short_curves = cull_short_curves(contour_curves)

    # 4. Fix self-intersections
    if fix_self_intersections:
        contour_curves = fix_self_intersections(contour_curves, intersection_threshold, layer_height)

    # 5. Sort by z value
    contour_curves = sort_by_z(contour_curves)

    # 6. Smooth curves
    elif smooth_curves:
        contour_curves = smooth_curves(contour_curves, layer_height, smoothing_factor)      

    # 7. Align seams
    contour_curves, seaming_points = align_seams(contour_curves)

    # 8. Divide curves into points
    division_points = divide_curves_in_points(contour_curves)

    return( contour_curves, 
            division_points, 
            seaming_points, 
            short_curves,)

def generate_ur_script(point_list, printing_speed, acceleration, fillet_radius):
    # add printing speed, acc and fillet radius to every point
    return ur_script

def shortest_path(curves, layer_height, max_branch_diff=25):
    """ Finds the shortest path between contour curves within a layer.
    """
    return curves

def get_bounding_box(mesh):

    """ Get bounding box of mesh
    """
    return min_z, max_z

def sort_by_z(curve_list):

    """ Sorts a list of curves by z value
    """
    return curve_list

def align_seams(curve_list):

    """ Aligns seams of curves
    """
    return aligned_curves, seaming_points

def match_curve_direction(curves):

    """ Matches all curves directions
    """
    return curves

def smooth_curves(curves, layer_height, smoothing_factor):

    """ Smoothens a list of curves with a predefined smoothing factor
    """
        return curves

def fix_self_intersections(curves, intersection_threshold, layer_height):

    """ Fixes self intersetions in curves
    """
    return fixed_curves 

def divide_curves_in_points(contour_curves, distance_between_points):

    """ Divides a curve into points at a certain distance. 
    """
    return pt_list