import numpy as np
import math
import matplotlib.pyplot as plt
import compas_slicer.utilities as utils
import logging
import progressbar

logger = logging.getLogger('logger')
__all__ = ['plot_layer_heights_variance',
           'compare_values_in_plot',
           'get_closest_vkeys']


def get_closest_vkeys(ppts, mesh):
    closest_vkeys = []
    with progressbar.ProgressBar(max_value=len(ppts)) as bar:
        for i, ppt in enumerate(ppts):
            closest_vkeys.append(utils.get_closest_mesh_vkey(mesh, ppt.pt))
            bar.update(i)
    return closest_vkeys


# def save_sorted_ppts_based_on_distance_from_target(ppts, target, path, filename):
#     logger.info('Sorting printpoints according to geodesic distance from target')
#     ppts_tupples = []
#     mesh = target.mesh
#     with progressbar.ProgressBar(max_value=len(ppts)) as bar:
#         for i, ppt in enumerate(ppts):
#             closest_vkey = utils.get_closest_mesh_vkey(mesh, ppt.pt)
#             ppts_tupples.append((ppt, closest_vkey, target.distance(closest_vkey)))
#             bar.update(i)
#
#     ppts_tupples = sorted(ppts_tupples, key=lambda v_tupple: v_tupple[2])
#     ppts = [t[0] for t in ppts_tupples]
#     closest_vkeys = [t[1] for t in ppts_tupples]
#
#     data = {
#         'ppts': {i: pp.to_data() for i, pp in enumerate(ppts)},
#         'closest_vkeys': {i: vkey for i, vkey in enumerate(closest_vkeys)}
#     }
#     utils.save_to_json(data, path, filename)


def plot_layer_heights_variance(ppts_layer_heights, label):
    x, values = get_differences_values(in_values=np.array(ppts_layer_heights))

    fig, axs = plt.subplots(1)
    axs.plot(x, values, label=label)
    axs.set_title('Abc')
    plt.legend()
    plt.xlabel('x')
    plt.ylabel('var(diff)')
    plt.grid(True)

    plt.show()


def compare_values_in_plot(values, labels):
    fig = plt.figure(figsize=(20, 20))

    for i, (value, label) in enumerate(zip(values, labels)):
        x, val = get_differences_values(np.array(value))
        plt.plot(x, val, figure=fig, color=(i / len(values), i / len(values), 1 - i / len(values)), label=label)
    plt.legend()

    plt.xlabel('x')
    plt.ylabel('var(diff)')
    plt.grid(True)
    plt.show()


def get_differences_values(in_values):
    values = in_values  # np.square(in_values - np.mean(in_values))
    subsample_n = 1
    new_len = len(values) - len(values) % subsample_n
    values = values[:new_len]
    values = np.mean(values.reshape(-1, subsample_n), axis=1)
    x = np.linspace(0, 1, len(values))
    return x, values
