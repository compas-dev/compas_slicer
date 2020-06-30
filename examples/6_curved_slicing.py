import os
from compas.datastructures import Mesh
import logging
import compas_slicer.utilities.utils as utils
from compas_slicer.slicers import CurvedSlicer
from compas_plotters import MeshPlotter
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)

########################
OBJ_INPUT_NAME = '_mesh.obj'
DATA_PATH = '../data/curved_slicing/surface/data'
########################

if __name__ == "__main__":

    ### --- Load initial_mesh
    mesh = Mesh.from_obj(os.path.join(DATA_PATH, OBJ_INPUT_NAME))

    ### --- Load boundaries and update vertex attributes
    low_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryLOW.json')
    high_boundary_vs = utils.load_from_json(DATA_PATH, 'boundaryHIGH.json')

    slicer = CurvedSlicer(mesh, low_boundary_vs, high_boundary_vs, DATA_PATH)

    slicer.slice_model()

    ### ----- Visualize
    plotter = MeshPlotter(mesh, figsize=(16, 10))
    plotter.draw_edges(width=0.15)
    plotter.draw_faces()
    plotter.draw_lines(slicer.get_contour_lines_for_plotter(color=(255, 0, 0)))
    plotter.show()

