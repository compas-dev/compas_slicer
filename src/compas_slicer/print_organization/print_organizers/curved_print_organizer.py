import logging
from compas.geometry import Polyline
from compas_slicer.print_organization.print_organizers.print_organizer import PrintOrganizer
from compas_slicer.geometry import PrintPoint



logger = logging.getLogger('logger')

__all__ = ['CurvedPrintOrganizer']


#############################################
#  RoboticPrintOrganizer
#############################################

class CurvedPrintOrganizer(PrintOrganizer):
    def __init__(self, slicer, mesh, extruder_toggle_type, DATA_PATH):
        self.slicer = slicer
        self.DATA_PATH = DATA_PATH

        #  topological sorting


        #  initialize print points
        self.printpoints_dict = {}
        self.create_printpoints_dict(mesh)
        self.set_extruder_toggle(extruder_toggle_type)


    def create_printpoints_dict(self, mesh):
        #  Without region split
        print('')
        logger.info('Creation of printpoints (curved slicer without region split)')

        mesh = self.slicer.mesh
        verticalLayers = self.slicer.layers

        #  --- Topological sort
        verticalLayers_dictList = []  # convert to format required for toposort. Fix this!! Very wrong!!
        for vl in verticalLayers:
            dictionary = {}
            for i, path in enumerate(vl.paths):
                dictionary['Isocurve_%d' % i] = path.points
            verticalLayers_dictList.append(dictionary)

        graph = topo_sort.SegmentsDirectedGraph(mesh, verticalLayers_dictList)
        all_orders = graph.get_all_topological_orders()
        logger.info('all_orders : ' + str(all_orders))
        selected_order = all_orders[0]
        logger.info('selected_order : ' + str(selected_order))

        root_boundary = Boundary(mesh, stratum_utils.get_mesh_vertex_coords_with_attribute(mesh, 'boundary', 1))

        for i, verticalLayer in enumerate(verticalLayers):
            self.printpoints_dict['layer_%d' % i] = {}

            #  --- Create stratum paths
            stratumPaths = []
            for path in verticalLayer.paths:
                path_points = path.points
                path_points.append(path_points[0])  # Close curve. Attention! Only works for closed curves!
                stratumPaths.append(StratumPath(Polyline(path_points), mesh))

            #  find the parent nodes of the current segment
            parents_of_segment = graph.get_parents_of_node(i)
            print('PARENTS : ', parents_of_segment)
            if len(parents_of_segment) == 0:
                boundary = root_boundary
                print(i, 'root')
            else:
                boundary_pts = []
                for parent_index in parents_of_segment:
                    parent_last_path = verticalLayers[parent_index].paths[-1]
                    boundary_pts.extend(parent_last_path.points)

                print(i, 'create boundary with %d points' % len(boundary_pts))
                boundary = Boundary(mesh, boundary_pts)

            stratum_path_collection = StratumPathCollection(stratumPaths, lower_boundary=boundary, mesh=mesh)
            stratum_path_collection.generate(first_layer_height=1.0)

            logger.info('stratum_path_collection.paths : ' + str(len(stratum_path_collection.paths)))

            #  convert to compas_slicer printpoints
            for j, stratum_path in enumerate(stratum_path_collection.paths):
                self.printpoints_dict['layer_%d' % i]['path_%d' % j] = \
                    [PrintPoint.from_data(stratum_printpoint.to_dict())
                     for stratum_printpoint in stratum_path.printpoints]

        logger.info('Completed printpoints generation')
