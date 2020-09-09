import compas_slicer
import logging
import stratum.utils.utils as stratum_utils
from compas_slicer.fabrication.print_organizers.robotic_print_organizer import RoboticPrintOrganizer

logger = logging.getLogger('logger')

__all__ = ['CurvedRoboticPrintOrganizer']

#############################################
### RoboticPrintOrganizer
#############################################

class CurvedRoboticPrintOrganizer(RoboticPrintOrganizer):
    def __init__(self, slicer, machine_model, material, extruder_toggle_type="always_on"):
        RoboticPrintOrganizer.__init__(self, slicer, machine_model, material, extruder_toggle_type)

    def create_printpoints(self):
        pass
        ### --- Load isocurves
        # isocurves_segments = utils.load_from_json(DATA_PATH, "isocurves_segments_" + str(k) + ".json")
        #
        # for i in range(len(isocurves_segments)):
        #     curves_dict = isocurves_segments['Segment_' + str(i)]
        #     ### --- find starting boundary
        #     vertex_clustering = VertexClustering(mesh, 'boundary', 1, DATA_PATH)
        #     boundary_pts = vertex_clustering.get_flattened_list_of_all_vertices()
        #     boundary = Boundary(mesh, boundary_pts)
        #     boundary.to_json(DATA_PATH, "boundary_" + str(i) + ".json")
        #
        #     ### --- Create paths
        #     paths = []
        #     for j in range(len(curves_dict)):
        #         path_points = curves_dict['Isocurve_' + str(j)]
        #         path_points.append(path_points[0])  # Close curve. Attention! Only works for closed curves!
        #         paths.append(Path(Polyline(path_points), mesh))
        #
        #     path_collection = Layer(paths=paths, lower_boundary=boundary, mesh=mesh)
        #     path_collection.generate(first_layer_height=1.0)
        #     utils.save_json(path_collection.to_dict(), DATA_PATH, "paths_collection_" + str(paths_index) + ".json")
        #     paths_index += 1

        # utils.interrupt()
