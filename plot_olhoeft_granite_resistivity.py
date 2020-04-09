# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 14:02:27 2019

@author: jpeacock
"""

import pandas as pd
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
from matplotlib import colors

def colorline(x, y, ax, z=None, cmap=plt.get_cmap('copper'),
              norm=plt.Normalize(0.0, 1.0), linewidth=4, alpha=1.0):
    """
    http://nbviewer.ipython.org/github/dpsanders/matplotlib-examples/blob/master/colorline.ipynb
    http://matplotlib.org/examples/pylab_examples/multicolored_line.html
    Plot a colored line with coordinates x and y
    Optionally specify colors in the array z
    Optionally specify a colormap, a norm function and a line width
    """

    # Default colors equally spaced on [0,1]:
    if z is None:
        z = np.linspace(0.0, 1.0, len(x))

    # Special case if a single number:
    if not hasattr(z, "__iter__"):  # to check for numerical input -- this is a hack
        z = np.array([z])

    z = np.asarray(z)

    segments = make_segments(x, y)
    lc = mcoll.LineCollection(segments, array=z, cmap=cmap, norm=norm,
                              linewidth=linewidth, alpha=alpha)

    ax.add_collection(lc)

    return lc


def make_segments(x, y):
    """
    Create list of line segments from x and y coordinates, in the correct format
    for LineCollection: an array of the form numlines x (points per line) x 2 (x
    and y) array
    """

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    return segments

def gradient_image(ax, extent, cmap_range=(0, 1), data_range=(0, 1),
                   cmap=plt.jet):
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
    a, b = cmap_range
    c, d = data_range
    
    grad = np.atleast_2d(np.linspace(c, d, 256))
    im = ax.imshow(grad, extent=extent, interpolation='bicubic',
                   alpha=1, vmin=a, vmax=b, cmap=cmap)
    return im

# =============================================================================
# color bar
# =============================================================================
#red to green to blue
ptcmapdict4 = {'red':  ((0.0, 0.0, 0.65),
                        (0.25, 1.0, 1.0),
                        (0.5, 1.0, 1.00),
                        (0.68,0.0, 0.0),
                        (1.0, 0.0, 0.0)),

               'green': ((0.0, 0.0, 0.0),
                         (0.25, 0.95, 0.95),
                         (0.5, 1.0, 1.0),
                         (0.68, .85, 0.85),
                         (1.0, 0.0, 0.0)),

              'blue':  ((0.0, 0.0, 0.0),
                        (0.25, 0.0, 0.0),
                        (0.5, 1.0, 1.0),
                        (0.68,1.0, 1.0),
                        (1.0, 0.45, 1.0))}
mt_res = colors.LinearSegmentedColormap('mt_res', ptcmapdict4, 256)

# =============================================================================
# plot
# =============================================================================
fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\granite_resistivity_olhoeft.csv"

rdf = pd.read_csv(fn)

res_dry = interpolate.interp1d(rdf.temperature, rdf.resistivity_dry)
res_wet = interpolate.interp1d(rdf.temperature, rdf.resistivity_wet)

g_index = np.nonzero(np.nan_to_num(rdf.resistivity_g))[0]
res_g = interpolate.interp1d(rdf.temperature[g_index],
                             rdf.resistivity_g[g_index])

t = np.logspace(np.log10(25), np.log10(1000), num=300)
tg = np.logspace(np.log10(25), np.log10(299), num=100)

fig = plt.figure(1, dpi=150)
fig.clf()
ax = fig.add_subplot(1, 1, 1)
#gradient_image(ax, (25, 1500, 0, 10**12), cmap='gray_r')
ax.set_facecolor((.7, .7, .7))

#s_dry = ax.scatter(rdf.temperature, 10**rdf.resistivity_dry, marker='+', s=8, 
#                   color=(0, .75, .75))
line_dry = colorline(t[::-1], 10**res_dry(t)[::-1], ax, cmap=mt_res,
                     norm=plt.Normalize(-1.00, .3))
line_wet = colorline(t[::-1], 10**res_wet(t)[::-1], ax, cmap=mt_res,
                     norm=plt.Normalize(0, 1.9))

line_g = colorline(tg[::-1], 10**res_g(tg)[::-1], ax, cmap=mt_res,
                     norm=plt.Normalize(-1, .5))

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_ylabel('Resistivity ($\Omega \cdot m$)')
ax.set_xlabel('Temperature ($^{\circ}C$)')
ax.grid(which='major', lw=.75, color=(1, 1, 1), ls=':')
ax.grid(which='minor', lw=.5, color=(.85, .85, .85), ls=':')

ax.axvspan(600, 1000, color=(.2, .2, .2)) # partial melt
ax.axvspan(300, 450, color=(.3, .3, .3)) # HTR
ax.axvspan(188, 300, color=(.45, .45, .45)) # NTR
ax.axhspan(75, 145, xmin=.54, xmax=.655, color=(0, .65, .85)) # NTR felsite
ax.axhspan(55, 105, xmin=.655, xmax=.75, color=(0, .75, .9)) # HTR felsite
ax.axhspan(20, 40, xmin=.805, xmax=.95, color=(.95, .9, 0)) # Partial melt

### labels
ax.text(200, 10.2**8, 'Dry Granite', va='center', ha='left', color=(1, 1, 1),
        rotation=-35, fontdict={'weight':'bold'})
ax.text(60, 1.5, 'Wet Granite (0.1 M NaCl)', va='baseline', ha='left',
        color=(1, 1, 1),rotation=-3, fontdict={'weight':'bold'})

ax.text(25, 10.5**4, 'Inada Granite (0.001 M KCl)', va='baseline', ha='left',
        color=(1, 1, 1), rotation=0, fontdict={'weight':'bold'})

ax.text(300, 170, 'GPC', va='baseline', ha='center', color=(1, 1, 1),
        rotation=0, fontdict={'weight':'bold'})
ax.text(330, 10**5, 'HTR', va='center', ha='left', color=(1, 1, 1),
        rotation=90, fontdict={'weight':'bold'})
ax.text(200, 10**5, 'NTR', va='center', ha='left', color=(1, 1, 1),
        rotation=90, fontdict={'weight':'bold'})
ax.text(750, 10**6, 'Partial Melt', va='center', ha='left', color=(1, 1, 1),
        rotation=90, fontdict={'weight':'bold'})
ax.text(500, 45, 'Heat Source', va='baseline', ha='left', color=(1, 1, 1),
        rotation=0, fontdict={'weight':'bold'})
ax.set_aspect('auto')
fig.tight_layout()

plt.show()