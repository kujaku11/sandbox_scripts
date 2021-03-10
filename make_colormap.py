# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 21:16:39 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

color_dict = {
    "red": (
        (0.0, 0.1, 0.15),
        (0.1, 0.45, 0.45), 
        (0.25, .85, .85),
        (0.35, 1.0, 1.0),
        (0.495, 1.0, 1.0),
        (0.505, 1.0, 0.9),
        (0.65, 0.3, 0.0),
        (0.75, 0.0, 0.0),
        (0.9, 0.0, 0.0),
        (1.0, 0.0, 0.0),
    ),
    "green": (
        (0.0, 0.0, 0.0),
        (0.1, 0.0, 0.0),
        (0.25, 0.45, 0.45),
        (0.35, .9, .9),
        (0.495, 1.0, 1.0),
        (0.505, 1.0, 1.0),
        (0.65, 1.0, 1.0),
        (0.75, 0.5, 0.5),
        (0.9, 0.0, 0.0),
        (1.0, 0.0, 0.0),
    ),
    "blue": (
        (0.0, 0.0, 0.0),
        (0.1, 0.0, 0.0),
        (0.25, 0.0, 0.0),
        (0.35, 0.5, 0.5),
        (0.4955, .95, .95),
        (0.505, 1.0, 1.0),
        (0.65, 1.0, 1.0),
        (0.75, .85, .85),
        (0.9, .45, .45),
        (1.0, .15, .25),
    ),
}

test_cmap = LinearSegmentedColormap("test", color_dict, 256)


def plot_examples(cmap):
    """
    Helper function to plot data with associated colormap.
    """
    np.random.seed(19680801)
    data = np.random.randn(30, 30)
    fig = plt.figure(1)
    fig.clf()
    ax = fig.add_subplot(1,1,1)

    psm = ax.pcolormesh(data, cmap=cmap, rasterized=True, vmin=-4, vmax=4)
    fig.colorbar(psm, ax=ax)
    plt.show()
    
plot_examples(test_cmap)