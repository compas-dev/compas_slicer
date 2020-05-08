import compas
from compas_am.slicing.printpath import Layer

import numpy as np
import mlrose

import logging
logger = logging.getLogger('logger')

def sort_shortest_path(layers):

    sorted_layers = []

    for layer in layers:
        coords_list = []
        for contour in layer.contours:
            for i, pt in enumerate(contour.points):
                if i == 0:
                    coords = (pt[0], pt[1])
                    coords_list.append(coords)
        
        problem_fit = mlrose.TSPOpt(length = len(coords_list), coords = coords_list, maximize = False)
        best_state, best_fitness = mlrose.genetic_alg(  problem_fit, 
                                                        pop_size = 200, 
                                                        mutation_prob = 0.1, 
                                                        max_attempts = 1, #still to be changed
                                                        random_state = 2)
       
        ordered_contours = [layer.contours[x] for x in best_state]

        l = Layer(ordered_contours, layer.infill_path, layer.support_path)
        sorted_layers.append(l)

    return sorted_layers 
    

if __name__ == "__main__":
    pass
