import logging
from compas.datastructures import Mesh
import os
import compas_slicer.utilities as slicer_utils
from compas_slicer.slicers import ScalarFieldContours


logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
OUTPUT_PATH = slicer_utils.get_output_directory(DATA_PATH)
MODEL = '_mesh.obj'

if __name__ == '__main__':

    # load mesh
    mesh = Mesh.from_obj(os.path.join(DATA_PATH, MODEL))

    # Load scalar field
    u = slicer_utils.load_from_json(DATA_PATH, 'scalar_field.json')

    # generate contours of scalar field
    contours = ScalarFieldContours(mesh, u, no_of_isocurves=40)
    contours.slice_model()
    slicer_utils.save_to_json(contours.to_data(), OUTPUT_PATH, 'isocontours.json')

    # PRINT ORGANIZATION DOES NOT WORK YET FOR SCALAR FIELD CONTOURS
