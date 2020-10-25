import numpy as np
import matplotlib.pyplot as plt

__all__ = ['plot_layer_heights_variance']

def plot_layer_heights_variance(printpoints):
    layer_heights = np.array([pp.layer_height for pp in printpoints])
    print(layer_heights.shape)
    avg = np.mean(layer_heights)
    sq_diff = np.square(layer_heights - avg)
    print(sq_diff.shape)
