import compas
import compas_am
import os
from compas.datastructures import Mesh
from compas_plotters import MeshPlotter

from compas_am.slicing.slicer import Slicer

import meshcut
import stl
import numpy as np

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FILE = os.path.abspath(os.path.join(DATA, 'bunny_LOW_RES.stl'))


if __name__ == "__main__":

    ### --- Load stl for meshcut and re-generate mesh
    m = stl.mesh.Mesh.from_file(FILE)
    # Flatten our vert array to Nx3 and generate corresponding faces array
    vertices = m.vectors.reshape(-1, 3)
    faces = np.arange(len(vertices)).reshape(-1, 3)
    # create meshcut mesh
    vertices, faces = meshcut.merge_close_vertices(vertices, faces)
    mesh = meshcut.TriangleMesh(vertices, faces)

    # get min and max z coordinates
    min_z, max_z = np.amin(vertices, axis=0)[2], np.amax(vertices, axis=0)[2]

    ### --- Slicer
    slicer = Slicer(mesh, min_z, max_z, slicer_type = "planar_meshcut", layer_height = 3.0)

    slicer.slice_model(create_contours = True, create_infill = False, create_supports = False)

    slicer.simplify_paths(threshold = 0.3)

    slicer.sort_paths(sorting_type = "shortest path")

    slicer.printout_info()

    slicer.save_contours_to_json(path = DATA, name = "bunny_low_res_stl_contours.json")


    ### ----- Visualize 

    mesh = Mesh.from_stl(FILE)

    plotter = MeshPlotter(mesh, figsize=(16, 10))
    plotter.draw_edges(width=0.15)
    plotter.draw_faces()
    plotter.draw_lines(slicer.get_contour_lines_for_plotter(color = (255,0,0)))
    plotter.show()