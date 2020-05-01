import compas
import compas_am
import os
from compas.datastructures import Mesh
from compas_plotters import MeshPlotter

from compas_am.slicing.slicer import Slicer

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FILE = os.path.abspath(os.path.join(DATA, 'vase.obj'))

if __name__ == "__main__":

    ### --- Load compas_mesh
    mesh = Mesh.from_obj(os.path.join(DATA, FILE))

    ### --- Slicer
    slicer = Slicer(mesh, slicer_type = "regular", layer_height = 1.0)
    print (slicer.contours[0].points)

    slicer.save_contours_in_Json(path = DATA, name = "vase_contours.json")

    # ### ----- Visualize 
    plotter = MeshPlotter(mesh, figsize=(16, 10))
    plotter.draw_edges(width=0.15)
    plotter.draw_faces()
    plotter.draw_lines(slicer.get_contour_lines_for_plotter(color = (255,0,0)))
    plotter.show()