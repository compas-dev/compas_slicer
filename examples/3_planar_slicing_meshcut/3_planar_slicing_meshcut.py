import compas
import compas_slicer
import os
from compas.datastructures import Mesh
from compas_plotters import MeshPlotter
from compas_slicer.polyline_simplification import simplify_paths_rdp
import compas_slicer.polyline_simplification.simplify_paths_curvature as simplify_paths_curvature
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.sorting import sort_per_segment, sort_per_shortest_path_mlrose
from compas_slicer.sorting import align_seams

######################## Logging
import logging

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = os.path.join(os.path.dirname(__file__), 'data')
FILE = os.path.abspath(os.path.join(DATA, 'branches_70.stl'))


def main():
    ### --- Load stl
    compas_mesh = Mesh.from_stl(FILE)

    ### --- Slicer
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_meshcut", layer_height=100.0)
    slicer.slice_model()
    slicer.printout_info()

    simplify_paths_rdp(slicer, threshold=0.2)
    sort_per_segment(slicer, max_layers_per_segment=False, threshold=slicer.layer_height * 1.6)
    align_seams(slicer)

    slicer.path_collections_to_json(filepath=DATA, name="slicer_data.json")

    ### ----- Visualize 
    plotter = MeshPlotter(compas_mesh, figsize=(16, 10))
    plotter.draw_edges(width=0.15)
    plotter.draw_faces()
    plotter.draw_lines(slicer.get_path_lines_for_plotter(color=(255, 0, 0)))
    plotter.show()


if __name__ == "__main__":
    main()
