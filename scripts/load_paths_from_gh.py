import os

from loguru import logger
from compas_slicer.utilities import load_from_json
from compas_slicer.slicers import PlanarSlicer
from compas_viewers.objectviewer import ObjectViewer


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
