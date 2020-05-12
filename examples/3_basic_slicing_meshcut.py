import compas
import compas_am
import os, sys
from compas.datastructures import Mesh
from compas_plotters import MeshPlotter

from compas_am.slicing.slicer import Slicer
from compas_am.input.input_geometry import InputGeometry

import meshcut
import stl
import numpy as np

######################## Logging
import logging
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FILE = os.path.abspath(os.path.join(DATA, 'branches_70.stl'))
# FILE = os.path.abspath(os.path.join(DATA, 'branches_70_short.obj'))


def main():

    ### --- Load stl
    compas_mesh = Mesh.from_stl(FILE)

    ### --- Slicer
    slicer = Slicer(compas_mesh, slicer_type = "planar_meshcut", layer_height = 10.0)

    slicer.slice_model(create_contours = True, create_infill = False, create_supports = False)

    slicer.simplify_paths(method = "uniform", threshold = 0.2)

    # slicer.sort_paths(method = "shortest_path", max_attempts=1)
 
    slicer.sort_paths(method = "per_segment", max_layers_per_segment=False)
    
    # slicer.align_seams(method = "seams_align")

    slicer.printout_info()

    slicer.save_contours_to_json(path = DATA, name = "branches_70_contours.json")

    ### ----- Visualize 
    plotter = MeshPlotter(compas_mesh, figsize=(16, 10))
    plotter.draw_edges(width=0.15)
    plotter.draw_faces()
    plotter.draw_lines(slicer.get_contour_lines_for_plotter(color = (255,0,0)))
    plotter.show()


if __name__ == "__main__":
    main()