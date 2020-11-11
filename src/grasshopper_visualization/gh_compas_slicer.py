import os
import sys
import json
from compas.datastructures import Mesh
import rhinoscriptsyntax as rs
from compas.datastructures import Mesh
import Rhino.Geometry as rg
from compas_ghpython.artists import MeshArtist
from compas.geometry import Frame


#######################################
# --- Slicer

def load_slicer(path, folder_name, json_name):
    """ Loads slicer data. """
    data = load_json_file(path, folder_name, json_name)

    mesh = None
    paths = []
    are_closed = []
    all_points = []

    if data:

        if 'mesh' in data:
            compas_mesh = Mesh.from_data(data['mesh'])
            artist = MeshArtist(compas_mesh)
            mesh = artist.draw()
        else:
            print('No mesh has been saved in the json file.')

        if 'layers' in data:
            layers_data = data['layers']

            for i in range(len(layers_data)):
                layer_data = layers_data[str(i)]
                paths_data = layer_data['paths']

                for j in range(len(paths_data)):
                    path_data = paths_data[str(j)]
                    pts = []

                    are_closed.append(path_data['is_closed'])

                    for k in range(len(path_data['points'])):
                        pt = path_data['points'][str(k)]
                        pt = rs.AddPoint(pt[0], pt[1], pt[2])  # re-create points
                        pts.append(pt)
                    all_points.extend(pts)
                    path = rs.AddPolyline(pts)

                    # # create contour per layer
                    # try:
                    #     path = rs.AddPolyline(pts)
                    # except:
                    #     print('Attention! Could not add polyline at layer %d, path %d with %d points ' % (
                    #         i, j, len(path_data['points'])))

                    paths.append(path)
        else:
            print('No layers have been saved in the json file. Is this the correct json?')

    return mesh, paths, are_closed, all_points


#######################################
# --- Printpoints

def load_printpoints(path, folder_name, json_name):
    """ Loads a dict of compas_slicer printpoints. """
    data = load_json_file(path, folder_name, json_name)

    # geometry data
    points = []
    frames = []
    layer_heights = []
    up_vectors = []
    mesh_normals = []
    closest_support = []

    # fabrication related data
    velocities = []
    wait_times = []
    blend_radiuses = []
    extruder_toggles = []
    feasibility = []

    if data:
        for i in range(len(data)):
            data_point = data[str(i)]

            # geometry related data
            point = rg.Point3d(data_point["point"][0], data_point["point"][1], data_point["point"][2])
            points.append(point)

            compas_frame = Frame.from_data(data_point["frame"])
            pt, x_axis, y_axis = compas_frame.point, compas_frame.xaxis, compas_frame.yaxis
            frame = rs.PlaneFromNormal(pt, rs.VectorCrossProduct(rg.Vector3d(x_axis[0], x_axis[1], x_axis[2]),
                                                                 rg.Vector3d(y_axis[0], y_axis[1], y_axis[2])))
            frames.append(frame)

            layer_heights.append(data_point["layer_height"])

            v = data_point["up_vector"]
            up_vector = rg.Vector3d(v[0], v[1], v[2])
            up_vectors.append(up_vector)

            v = data_point["mesh_normal"]
            mesh_normal = rg.Vector3d(v[0], v[1], v[2])
            mesh_normals.append(mesh_normal)

            cp = data_point["closest_support_pt"]
            if cp:
                cp_pt = rg.Point3d(cp[0], cp[1], cp[2])
                closest_support.append(cp_pt)

            # fabrication related data
            velocities.append(data_point["velocity"])
            wait_times.append(data_point["wait_time"])
            blend_radiuses.append(data_point["blend_radius"])
            extruder_toggles.append(data_point["extruder_toggle"])
            feasibility.append(data_point["is_feasible"])

    return points, frames, layer_heights, up_vectors, mesh_normals, closest_support, \
           velocities, wait_times, blend_radiuses, extruder_toggles, feasibility


#######################################
# --- Lightweight path visualization

def lightweight_path_visualization(points, extruder_toggles, domain_start, domain_end, diameter, pipe_resolution):
    """ Visualize print paths with simple lines or pipes. """
    # check input
    assert len(points) == len(extruder_toggles), \
        'Wrong length of input lists'

    print_path_pipes = []
    travel_path_lines = []

    domain_end = min(domain_end, len(points)) # make sure domain_end does not exceed len of pts

    points = points[domain_start:domain_end]
    extruder_toggles = extruder_toggles[domain_start:domain_end]
    for i in range(len(points) - 1):
        if extruder_toggles[i]:
            line = rg.Curve.CreateControlPointCurve([points[i], points[i + 1]])  # create line
            pipe = rg.Mesh.CreateFromCurvePipe(line, diameter / 2, pipe_resolution, 1, rg.MeshPipeCapStyle.None, True)
            print_path_pipes.append(pipe)
        else:
            line = rg.Curve.CreateControlPointCurve([points[i], points[i + 1]])
            travel_path_lines.append(line)  # add to travel path list

    return print_path_pipes, travel_path_lines


#######################################
# --- Render path visualization

def render_path_visualization(points, mesh_normals, layer_heights, up_vectors, extruder_toggles, cross_section):
    """ Visualize print paths with simple loft surfaces. """

    # check input
    assert len(points) == len(mesh_normals) == len(layer_heights) == len(up_vectors) == len(extruder_toggles),\
    'Wrong length of input lists'

    loft_surfaces = []
    travel_path_lines = []

    if points[0] and mesh_normals[0] and layer_heights[0] and up_vectors[0]: # check if any of the values are None

        # transform and scale cross sections accordingly
        cen = rs.CurveAreaCentroid(cross_section)[0]
        origin_plane = rg.Plane(cen, rg.Vector3d(1, 0, 0), rg.Vector3d(0, 0, 1))

        target_planes = []
        for i, pt in enumerate(points):
            target_plane = rg.Plane(pt, mesh_normals[i], up_vectors[i])
            target_planes.append(target_plane)

        cross_sections = []
        for h, target_plane in zip(layer_heights, target_planes):
            section = rs.ScaleObject(rs.CopyObject(cross_section), origin=cen, scale=[0.9 * h, 1, 0.9 * h])
            T = rg.Transform.PlaneToPlane(origin_plane, target_plane)
            rs.TransformObject(section, T)
            cross_sections.append(section)

        loft_surfaces = []
        travel_path_lines = []

        for i in range(len(points) - 1):
            if extruder_toggles[i]:
                loft = rs.AddLoftSrf([cross_sections[i], cross_sections[i + 1]])
                if loft:
                    loft_surfaces.append(loft[0])
            else:
                line = rg.Curve.CreateControlPointCurve([points[i], points[i + 1]])
                travel_path_lines.append(line)  # add to travel path list

    else:
        print('At least one of the inputs that you have provided are invalid. ')

    return loft_surfaces, travel_path_lines


#######################################
# --- Tool visualization

def tool_visualization(origin_coords, mesh, planes, i):
    """ Visualize example tool motion. """

    i = min(i, len(planes)-1) # make sure i doesn't go beyond available number of planes
    passed_path = None

    if planes[0]:
        origin = [float(origin_coords[0]), float(origin_coords[1]) , float(origin_coords[2])]
        o = rg.Point3d(origin[0], origin[1], origin[2])
        x = rg.Vector3d(1, 0, 0)
        z = rg.Vector3d(0, 0, -1)

        ee_frame = rg.Plane(o,x,z)
        target_frame = planes[i]

        T = rg.Transform.PlaneToPlane(ee_frame, target_frame)
        mesh = rs.TransformObject(rs.CopyObject(mesh), T)

        passed_path = rs.AddPolyline([plane.Origin for plane in planes[:i+1]])

    else:
        print('The planes you have provided are invalid. ')

    return mesh, passed_path



##############################################
# --- gh_utilities

def load_json_file(path, folder_name, json_name):
    """ Loads data from json. """

    filename = os.path.join(os.path.join(path), folder_name, 'output', json_name)
    data = None

    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        print("Loaded Json: '" + filename + "'")
    else:
        print("Attention! Filename: '" + filename + "' does not exist. ")

    return data


if __name__ == "__main__":
    pass
