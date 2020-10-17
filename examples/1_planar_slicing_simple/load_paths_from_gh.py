import os
from compas.datastructures import Mesh
from compas.geometry import Point, Frame

from compas_slicer.utilities import load_from_json
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import generate_brim
from compas_slicer.post_processing import spiralize_contours
from compas_slicer.post_processing import seams_align
from compas_slicer.post_processing import seams_smooth, unify_paths_orientation
from compas_slicer.print_organization import RoboticPrintOrganizer
from compas_slicer.print_organization import RobotPrinter
from compas_viewers.objectviewer import ObjectViewer
from compas_slicer.post_processing import move_mesh_to_point, simplify_paths_rdp
import time

######################## Logging
import logging

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)


########################

def main():
    ### --- Data paths
    DATA = os.path.join(os.path.dirname(__file__), 'data')
    INPUT_FILE = 'paths_from_gh.json'

    slicer = PlanarSlicer.from_data(load_from_json(DATA, INPUT_FILE))

    ### --- Visualize using the compas_viewer
    viewer = ObjectViewer()
    viewer.view.use_shaders = False
    slicer.visualize_on_viewer(viewer, visualize_mesh=False, visualize_paths=True)

    viewer.update()
    viewer.show()

if __name__ == '__main__':
    main()
