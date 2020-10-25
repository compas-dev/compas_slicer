import numpy as np
import matplotlib.pyplot as plt
import compas_slicer.utilities as utils
import logging

logger = logging.getLogger('logger')
__all__ = ['plot_layer_heights_variance',
           'compare_layer_heights_variance']


def sort_based_on_distance_from_target(ppts, target):
    logger.info('Sorting printpoints according to geodesic distance from target')
    ppts_tupples = []
    mesh = target.mesh
    for ppt in ppts:
        closest_vkey = utils.get_closest_mesh_vkey(mesh, ppt.pt)
        ppts_tupples.append((ppt, target.distance(closest_vkey)))

    ppts_tupples = sorted(ppts_tupples, key=lambda v_tupple: v_tupple[1])
    return [t[0] for t in ppts_tupples]


def plot_layer_heights_variance(ppts_layer_heights, label):
    layer_heights = np.array(ppts_layer_heights)
    print(layer_heights.shape)
    avg = np.mean(layer_heights)
    sq_diff = np.square(layer_heights - avg)
    print(sq_diff.shape)

    all_ks = np.linspace(0, 1, len(ppts_layer_heights))

    fig, axs = plt.subplots(1)
    axs.plot(all_ks, sq_diff, label=label)
    axs.set_title('Abc')
    # axs[1].bar(sq_diff, label=label)
    # axs[1].set_title('Cba')
    # plt.plot(all_ks, vars_vectorized, 'x-', label='vectorized')
    plt.legend()
    plt.xlabel('k')
    plt.ylabel('var(diff)')
    plt.grid(True)

    plt.show()


def compare_layer_heights_variance(h1, h2, label1, label2):
    h1 = np.array(h1)
    h2 = np.array(h2)
    sq_diff1 = np.square(h1 - np.mean(h1))
    sq_diff2 = np.square(h2 - np.mean(h2))

    all_ks1 = np.linspace(0, 1, len(h1))
    all_ks2 = np.linspace(0, 1, len(h2))

    plt.plot(all_ks1, sq_diff1, color=(1, 0, 0), label=label1)
    plt.plot(all_ks2, sq_diff2, color=(0, 0, 1), label=label2)

    # plt.plot(all_ks, vars_vectorized, 'x-', label='vectorized')
    plt.legend()
    plt.xlabel('k')
    plt.ylabel('var(diff)')
    plt.grid(True)

    plt.show()
