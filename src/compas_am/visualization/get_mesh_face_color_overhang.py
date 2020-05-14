import compas
from compas.datastructures import Mesh
from compas.geometry import Vector, angle_vectors

from math import degrees

def get_mesh_face_color_overhang(mesh, max_angle=45, mode="adaptive", infill=True):
    """Assigns a mesh face color based on the overhang angle. 
    Use the resulting list as an input for the compas Artist (Rhino, Blender)

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        Input mesh.
    max_angle : int
        Maximum overhang possible with fabrication machine.
    mode : str
        "adaptive", "fixed"

        The visualisation mode. Adaptive mode colors the mesh based on the maximum angle,
        whereas Fixed mode uses a standard gradient from 0 - 90 degrees. 
        
        Adaptive mode colour settings: 
            Green:  0 degree overhang
            Yellow: 0.5x max_angle
            Red:    Max angle 
            Black:  > Max angle (not printable)
        Fixed mode colour settings:
            Green:  0 degree overhang
            Yellow: 45 degree overhang
            Red:    90 degree overhang
    infill : boolean
        True if printing a solid object (with infill), False if printing only contours (no infill).

    Returns
    -------
    list
        List of RGB colour values for the Mesh faces. 
        Use as an input for a compas Artist.
    """

    if not (0 <= max_angle <= 90):
        raise NameError("Max angle needs to be between 0-90 degrees.")
    if max_angle == 0:
        # makes sure that no division by 0 occurs
        max_angle = 1E-10

    color_list = []

    for fkey in mesh.faces():
        # get normal and calculate angle compared to Z direction
        normal = mesh.face_normal(fkey)
        angle = degrees(angle_vectors(normal, Vector(0.0, 0.0, 1.0)))

        # if structure has infills all angles < 90 are not overhangs
        if infill == False:
            angle = abs(90-angle)
        elif infill == True:
            if angle < 90:
                angle = 0
            else:
                angle = abs(90-angle)

        if mode == "adaptive":
            if angle > max_angle:
                # append black color
                color_list.append((1,1,1))
            else:
                if angle < max_angle/float(2):
                    # color gradient: green - yellow
                    R = int(angle * (256/(max_angle/float(2))))
                    color_list.append((R,255,0))
                elif max_angle/float(2) < angle <= max_angle:
                    # color gradient: yellow - red
                    G = int((angle-(max_angle/float(2))) * (256/(max_angle/float(2))))
                    color_list.append((255,255-G,0))
        elif mode == "fixed":
            if angle <= 45:
                # color gradient: green - yellow
                R = int(angle * (256/45))
                color_list.append((R,255,0))
            elif angle > 45:
                # color gradient: yellow - red
                G = int((angle-45) * (256/45))
                color_list.append((255,255-G,0))
        else:
            raise NameError("Invalid visualisation mode : " + mode)
    
    return color_list
                