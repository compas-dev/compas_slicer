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

import time

######################## Logging
import logging
logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)
######################## 

DATA = os.path.join(os.path.dirname(__file__), 'data')
FILE = os.path.join(DATA, 'branches_70.stl')

start_time = time.time()

def main():
    ### --- Load stl
    compas_mesh = Mesh.from_stl(FILE)

    ### --- Slicer
    slicer = PlanarSlicer(compas_mesh, slicer_type="planar_cgal", layer_height=150.0)
    slicer.slice_model(create_contours=True, create_infill=False, create_supports=False)
    slicer.printout_info()

    # simplify_paths_rdp(slicer, threshold=0.2)
    # sort_per_segment(slicer, max_layers_per_segment=False, threshold=slicer.layer_height * 1.6)
    # align_seams(slicer)

    end_time = time.time()
    print("Total elapsed time", round(end_time - start_time, 2), "seconds")

    slicer.to_json(DATA, 'slicer_data.json')

    slicer.layers_to_json(DATA, 'slicer_data_layers.json')

    ### ----- Visualize 
    # plotter = MeshPlotter(compas_mesh, figsize=(16, 10))
    # plotter.draw_edges(width=0.15)
    # plotter.draw_faces()
    # plotter.draw_lines(slicer.get_contour_lines_for_plotter(color=(255, 0, 0)))
    # plotter.show()


if __name__ == "__main__":
    main()
