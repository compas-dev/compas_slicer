import sys

from compas.geometry import Polyline

from compas_slicer.slicers import BaseSlicer
from compas_slicer.geometry import Segment
import compas_slicer.utilities.utils as utils
from compas_slicer.geometry import Path

import logging
logger = logging.getLogger('logger')

try:
    import stratum.region_split.topological_sort as topo_sort
    # from stratum.printpaths.path import Path
    from stratum.printpaths.boundary import Boundary
    from stratum.printpaths.path_collection import PathCollection
    from stratum.isocurves.compound_target import CompoundTarget
    from stratum.isocurves.marching_triangles import MarchingTriangles, find_desired_number_of_isocurves
    import stratum.utils.utils as stratum_utils
except:
    pass


__all__ = ['CurvedSlicer']


class CurvedSlicer(BaseSlicer):
    def __init__(self, mesh, low_boundary_vs, high_boundary_vs, DATA_PATH):
        BaseSlicer.__init__(self, mesh)

        if not 'stratum' in sys.modules:
            for key in sys.modules:
                print (key)
            raise ValueError('Attention! You need to install stratum to use the curved slicer')

        self.min_layer_height = 0.2
        self.max_layer_height = 2.0
        self.DATA_PATH = DATA_PATH

        ### --- Update vertex attributes
        self.mesh.update_default_vertex_attributes({'boundary': 0})
        for vkey, data in self.mesh.vertices(data=True):
            if vkey in low_boundary_vs:
                data['boundary'] = 1
            elif vkey in high_boundary_vs:
                data['boundary'] = 2

    def slice_model(self, create_contours=True, create_infill=False, create_supports=False):
        if create_infill or create_supports:
            raise NotImplementedError

        if create_contours:
            target_0 = CompoundTarget(self.mesh, 'boundary', 1, self.DATA_PATH, is_smooth=False)
            target_1 = CompoundTarget(self.mesh, 'boundary', 2, self.DATA_PATH, is_smooth=False)
            target_0.save_distances("distances_0.json")
            target_1.save_distances("distances_1.json")

            ## Marching Triangles
            print('')
            # number_of_curves = find_desired_number_of_isocurves(target_0, target_1)
            number_of_curves = 5
            marching_triangles = MarchingTriangles(self.mesh, target_0, target_1, number_of_curves)

            ## Save to Json
            stratum_utils.isocurves_segments_to_json(marching_triangles.segments, self.DATA_PATH,
                                                     "isocurves_segments.json")


            ## convert stratum entities to compas_slicer entities
            ## Not particularly useful
            segments = []
            for i, stratum_segment in enumerate(marching_triangles.segments):
                s = Segment(i)
                segments.append(s)
                for isocurve in stratum_segment.isocurves:
                    s.append_(Path(isocurve.points, is_closed=True))

            self.print_paths = segments

    def generate_printpoints(self):
        # segments = self.print_paths
        ## reload from Json. Like that we don't have to regenerate every time
        segments_data = stratum_utils.load_from_json(self.DATA_PATH, "isocurves_segments.json")
        segments = [segments_data['Segment_' + str(i)] for i in range(len(segments_data))]

        ## Topological sort
        print('')
        graph = topo_sort.SegmentsDirectedGraph(self.mesh, segments)
        all_orders = graph.get_all_topological_orders()
        selected_order = all_orders[0]
        logger.info('selected_order : ' + str(selected_order))

        ## Generate paths with printpoints
        root_boundary = Boundary(self.mesh,
                                 stratum_utils.get_mesh_vertex_coords_with_attribute(self.mesh, 'boundary', 1))
        paths_index = 0

        for i, segment in enumerate(segments):
            print('')
            ### --- Create paths
            paths = []
            for j in range(len(segment)):
                path_points = segment['Isocurve_' + str(j)]
                path_points.append(path_points[0])  # Close curve. Attention! Only works for closed curves!
                paths.append(Path(Polyline(path_points), self.mesh))

            ## find the parent nodes of the current segment and create boundary
            parents_of_node = graph.get_parents_of_node(i)
            if len(parents_of_node) == 0:  # then use start boundary
                boundary = root_boundary
            else:  # then create new boundary with the points of the last isocurve of the parent segment
                boundary_pts = []
                for parent_index in parents_of_node:
                    parent = segments[parent_index]
                    last_crv_pts = parent['Isocurve_' + str(len(parent) - 1)]
                    boundary_pts.extend(last_crv_pts)
                boundary = Boundary(self.mesh, boundary_pts)

            path_collection = PathCollection(paths, lower_boundary=boundary, mesh=self.mesh)
            path_collection.generate(first_layer_height=1.0)
            utils.save_to_json(path_collection.to_dict(), self.DATA_PATH, "paths_collection" + str(paths_index) + ".json")
            paths_index += 1



if __name__ == "__main__":
    pass
