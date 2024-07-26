# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 11:37:28 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np

# import PIL.Image
from matplotlib.image import imread
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import pyplot as plt
import matplotlib.colors

from mtpy.imaging.mtplot_tools.map_interpolation_tools import (
    griddata_interpolate,
)
from pyevtk.hl import pointsToVTK
from scipy.signal import medfilt2d


# import colorsort as csort

# =============================================================================

moho_colormap = imread(
    r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\inv_05_topo\moho_color_bar.png"
)[0, :, :]

moho_colormap = np.delete(moho_colormap, np.s_[172], 0)

moho_cmap = LinearSegmentedColormap.from_list(
    "moho_depth", moho_colormap, N=moho_colormap.shape[0]
)

moho_image = imread(
    r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\inv_05_topo\moho_depth_li_edited.png"
)


norm = matplotlib.colors.Normalize(15, 35)
depths = np.linspace(15, 35, 100)
moho_colors = plt.get_cmap(moho_cmap)(norm(depths))

tol = 0.25
moho_depth = np.zeros(moho_image.shape[0:2])
for ii in range(moho_image.shape[0]):
    for jj in range(moho_image.shape[1]):
        c = moho_image[ii, jj]
        index_values = np.where(
            (c[0] + tol >= moho_colors[:, 0])
            & (c[0] - tol <= moho_colors[:, 0])
            & (c[1] + tol >= moho_colors[:, 1])
            & (c[1] - tol <= moho_colors[:, 1])
            & (c[2] + tol >= moho_colors[:, 2])
            & (c[2] - tol <= moho_colors[:, 2])
        )
        try:
            index = index_values[0][0]
            if depths[index] < 18:
                moho_depth[ii, jj] = np.NAN
            else:
                moho_depth[ii, jj] = depths[index]
        except IndexError:
            moho_depth[ii, jj] = np.NAN
            continue

### need to get rid of the volcano

x = np.arange(moho_depth.shape[1])
y = np.arange(moho_depth.shape[0])
X, Y = np.meshgrid(x, y)
is_nan = np.isnan(moho_depth).flatten()
plot_x, plot_y, values = griddata_interpolate(
    np.delete(X.flatten(), is_nan),
    np.delete(Y.flatten(), is_nan),
    np.delete(moho_depth.flatten(), is_nan),
    x,
    y,
    interpolation_method="linear",
)

values = medfilt2d(values, (55, 55))
values[np.where(values < 18)] = np.nan

fig = plt.figure(1)
fig.clf()
ax1 = fig.add_subplot(1, 3, 1)
im = ax1.imshow(moho_image, cmap=moho_cmap, vmin=15, vmax=35)
cb = plt.colorbar(im)
ax2 = fig.add_subplot(1, 3, 2)
im2 = ax2.imshow(moho_depth, cmap=moho_cmap, vmin=15, vmax=35)
cb2 = plt.colorbar(im2)
ax3 = fig.add_subplot(1, 3, 3)
im3 = ax3.imshow(values, cmap=moho_cmap, vmin=15, vmax=35)
cb3 = plt.colorbar(im3)
plt.show()

top_left = {"east": 475481, "north": 4.35489e6}
bottom_right = {"east": 589245, "north": 4.20548e6}

easting = np.linspace(top_left["east"], bottom_right["east"], values.shape[1])
northing = np.linspace(
    top_left["north"], bottom_right["north"], values.shape[0]
)

east, north = np.meshgrid(easting, northing)

pointsToVTK(
    r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\modem_inv\inv_05_topo\moho_depth_li",
    east.flatten(),
    north.flatten(),
    -values.flatten() * 1000 - 1000,
    {"depth": values.flatten() - 1},
)
