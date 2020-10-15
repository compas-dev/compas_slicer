import os
from compas.datastructures import Mesh
from compas_rhino.artists import MeshArtist
from scripts.artists import get_mesh_face_color_overhang

# reload required for Rhino 
import scripts.artists
reload(scripts.artists)

DATA = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
FILE = os.path.abspath(os.path.join(DATA, 'bunny_low_res.stl'))

def main():
    #####################################
    ### NOTE: Run this file in Rhino. ### 
    #####################################

    ### --- Load stl
    mesh = Mesh.from_stl(FILE)

    ### --- Get color list
    color_list = get_mesh_face_color_overhang(mesh, max_angle=85, mode="adaptive", infill=False)

    ### --- Create Rhino artist
    artist = MeshArtist(mesh, layer='COMPAS::MeshArtist')
    artist.clear_layer() 
    artist.draw_faces(color={key: color_list[i] for i, key in enumerate(mesh.faces())})
    artist.redraw()
    
if __name__ == "__main__":
    main()

