import compas
import compas_am
import os
from compas.datastructures import Mesh
from compas_plotters import MeshPlotter
from compas_am.slicing.slicer import Slicer

######################## Logging
import logging
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FILE = os.path.abspath(os.path.join(DATA, 'vase.obj'))


if __name__ == "__main__":

    ### --- Load compas_mesh
    compas_mesh = Mesh.from_obj(os.path.join(DATA, FILE))

    ### --- Slicer
    slicer = Slicer(compas_mesh, slicer_type = "planar_numpy", layer_height = 1.0)

    slicer.slice_model(create_contours = True, create_infill = False, create_supports = False)

    slicer.simplify_paths(threshold = 0.3)

    slicer.sort_paths(sorting_type = "shortest path")

    slicer.printout_info()

    slicer.save_contours_to_json(path = DATA, name = "vase_contours.json")


    # ### ----- Visualize 
    plotter = MeshPlotter(compas_mesh, figsize=(16, 10))
    plotter.draw_edges(width=0.15)
    plotter.draw_faces()
    plotter.draw_lines(slicer.get_contour_lines_for_plotter(color = (255,0,0)))
    plotter.show()