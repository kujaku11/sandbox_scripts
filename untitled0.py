# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 10:42:51 2019

@author: jpeacock
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

csv_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\rock_resistivity_summary.csv"

def gradient_image(ax, extent, direction=0.3, cmap_range=(0, 1), **kwargs):
    """
    Draw a gradient image based on a colormap.

    Parameters
    ----------
    ax : Axes
        The axes to draw on.
    extent
        The extent of the image as (xmin, xmax, ymin, ymax).
        By default, this is in Axes coordinates but may be
        changed using the *transform* kwarg.
    direction : float
        The direction of the gradient. This is a number in
        range 0 (=vertical) to 1 (=horizontal).
    cmap_range : float, float
        The fraction (cmin, cmax) of the colormap that should be
        used for the gradient, where the complete colormap is (0, 1).
    **kwargs
        Other parameters are passed on to `.Axes.imshow()`.
        In particular useful is *cmap*.
    """
    phi = direction * np.pi / 2
    v = np.array([np.cos(phi), np.sin(phi)])
    X = np.array([[v @ [1, 0], v @ [1, 1]],
                  [v @ [0, 0], v @ [0, 1]]])
    a, b = cmap_range
    X = a + (b - a) / X.max() * X
    im = ax.imshow(X, extent=extent, interpolation='bicubic',
                   vmin=0, vmax=1, **kwargs)
    return im


def gradient_bar(ax, x, y, width=0.5, bottom=0):
    for left, top in zip(x, y):
        right = left + width
        gradient_image(ax, extent=(left, right, bottom, top),
                       cmap=plt.cm.Blues_r, cmap_range=(0, 0.8))

# =============================================================================
# plot bars on color scale
# =============================================================================
df = pd.read_csv(csv_fn)
        
#xmin, xmax = xlim = 0, 10
#ymin, ymax = ylim = 0, 1

fig, ax = plt.subplots()

#ax.set(xlim=xlim, ylim=ylim, autoscale_on=False)

# background image
#gradient_image(ax, direction=0, extent=(0, 1, 0, 1), transform=ax.transAxes,
#               cmap=plt.cm.Oranges, cmap_range=(0.1, 0.6))

for row in df.iterrows():
    bar_extent = (row.pdf_50_min, row.pdf_50_max, row.index, row.index*1.5)
    gradient_image(ax, extent=bar_extent, cmap=plt.cm.jet_r, 
                   cmap_range(1, 500))
ax.set_aspect('auto')
plt.show()