import warnings

# workaround to import six since from sklarn.externals import six is deprecated
import six
import sys
sys.modules['sklearn.externals.six'] = six

warnings.filterwarnings("ignore")
import mlrose

warnings.filterwarnings("default")
import logging

logger = logging.getLogger('logger')

__all__ = ['sort_per_shortest_path_mlrose']


def sort_per_shortest_path_mlrose(slicer,
                              population_size=200,
                              mutation_probability=0.1,
                              max_attempts=10,
                              random_state=None):

    """Attempts to find the shortest path between the contours in a layer,
    most useful when dealing with many contours within one layer. 
    Heavily increases computation time but reduces printing time. 

    Based on the Travelling Salesperson Problem (TSP), makes use of 
    a Randomized Optimization Algorithm as implemented in mlrose:

    Hayes, G. (2019). mlrose: Machine Learning, Randomized Optimization 
    and SEarch package for Python. https://github.com/gkhayes/mlrose.

    Parameters
    ----------
    layers : list
        An instance of the compas_slicer.slicing.printpath.Layer class.
    population_size : int
        Population size.
    mutation_probability : float
        Probability of mutation.
    max_attempts : int
        Maximum amount of attempts per step.
    random_state : int
        Randomised initialisation state.


    Examples
    --------
        Based on: "Solving Travelling Salesperson Problems with Python" by G. Hayes
        https://towardsdatascience.com/solving-travelling-salesperson-problems-with-python-5de7e883d847

        import mlrose
        import numpy as np

        coords_list = [(1, 1), (4, 2), (5, 2), (6, 4), (4, 4), (3, 6), (1, 5), (2, 3)]

        problem_no_fit = mlrose.TSPOpt(length = 8, coords = coords_list, maximize=False)
        best_state, best_fitness = mlrose.genetic_alg(problem_no_fit, random_state = 2)
                               
        print('The best state found is: ', best_state)
        print('The fitness at the best state is: ', best_fitness)
    """

    logger.info("Sorting per shortest path using mlrose")

    layers = slicer.print_paths

    for layer in layers:
        coords_list = []
        for contour in layer.contours:
            for i, point in enumerate(contour.points):
                if i == 0:
                    coords = (point[0], point[1])
                    coords_list.append(coords)

        problem_no_fit = mlrose.TSPOpt(length=len(coords_list), coords=coords_list, maximize=False)
        best_state, best_fitness = mlrose.genetic_alg(problem_no_fit,
                                                      pop_size=population_size,
                                                      mutation_prob=mutation_probability,
                                                      max_attempts=max_attempts,
                                                      random_state=random_state)

        ordered_contours = [layer.contours[x] for x in best_state]
        layer.contours = ordered_contours

        ##TODO: 
        # if layer.infill_paths: ...
        # if layer.support_paths: ...

    slicer.print_paths = layers


if __name__ == "__main__":
    pass
