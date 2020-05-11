import compas
import os, sys
from compas.datastructures import Mesh
from compas_rhino.artists import MeshArtist

from math import degrees
from compas.geometry import Vector, angle_vectors

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FILE = os.path.abspath(os.path.join(DATA, 'bunny_low_res.stl'))

def rhino_color_mesh_faces_by_overhang_angle(max_angle=45, mode="adaptive", infill=True):
    """Imports a compas mesh and assigns a mesh face color based on the 
    overhang angle
    
    NOTE: Run this file in Rhino.

    Parameters
    ----------
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
    """

    ### --- Load stl
    compas_mesh = Mesh.from_stl(FILE)

    color_list = []

    for fkey in compas_mesh.faces():
        # get normal and calculate angle compared to Z direction
        normal = compas_mesh.face_normal(fkey)
        angle = degrees(angle_vectors(normal, Vector(0.0, 0.0, 1.0)))

        # if structure has infills all angles < 90 are printable
        if infill == False:
            angle = abs(90-angle)
        elif infill == True:
            angle = degrees(angle_vectors(normal, Vector(0.0, 0.0, 1.0)))
            if angle < 90:
                angle = 0
            else:
                angle = abs(90-angle)

        if mode == "adaptive":
            if angle > max_angle:
                # append black color
                color_list.append((1,1,1))
            else:
                if angle < max_angle/2:
                    # color gradient: green - yellow
                    R = int(angle * (256/(max_angle/2)))
                    color_list.append((R,255,0))
                elif max_angle/2 < angle < max_angle:
                    # color gradient: yellow - red
                    G = int((angle-(max_angle/2)) * (256/(max_angle/2)))
                    color_list.append((255,255-G,0))
        elif mode == "fixed":
            if angle < 45:
                # color gradient: green - yellow
                R = int(angle * (256/45))
                color_list.append((R,255,0))
            elif angle > 45 < 90:
                # color gradient: yellow - red
                G = int((angle-45) * (256/45))
                color_list.append((255,255-G,0))
        else:
            raise NameError("Invalid visualisation mode : " + mode)
                
    artist = MeshArtist(compas_mesh, layer='COMPAS::MeshArtist')
    artist.clear_layer() 
    artist.draw_faces(color={key: color_list[i] for i, key in enumerate(compas_mesh.faces())})
    artist.redraw()
    
if __name__ == "__main__":
    rhino_color_mesh_faces_by_overhang_angle()