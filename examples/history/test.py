import compas
from compas.datastructures import Mesh
from compas.geometry import centroid_points
from compas.geometry import distance_point_point
from compas.geometry import scalarfield_contours_numpy

mesh = Mesh.from_obj(compas.get('faces.obj'))

points = [mesh.vertex_coordinates(key) for key in mesh.vertices()]
centroid = centroid_points(points)
distances = [distance_point_point(point, centroid) for point in points]

xy = [point[0:2] for point in points]

levels, contours = scalarfield_contours_numpy(xy, distances)

for i in range(len(contours)):
    level = levels[i]
    contour = contours[i]
    print(level)
    for path in contour:
        for polygon in path:
            print(polygon)