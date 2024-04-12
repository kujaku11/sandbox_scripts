# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 15:25:48 2019

@author: jpeacock
"""

from mtpy.modeling import modem
import numpy as np
import matplotlib.pyplot as plt
from mtpy.utils import array2raster

mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\gz_steam_field_inv06.rho"
dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\gz_modem_data_z03_topo.dat"

d_obj = modem.Data()
d_obj.read_data_file(dfn)

m_obj = modem.Model()
m_obj.read_model_file(mfn)
m_obj.res_model[np.where(m_obj.res_model > 10000)] = np.nan

c_map = np.zeros_like(m_obj.res_model[:, :, 0])

for x_index in range(m_obj.res_model.shape[0]):
    for y_index in range(m_obj.res_model.shape[1]):
        c_map[x_index, y_index] = np.nanmedian(
            m_obj.res_model[x_index, y_index, :]
        )


x_plot, y_plot = np.meshgrid(m_obj.plot_east - 1150, m_obj.plot_north - 2300)

fig = plt.figure(2)
fig.clf()

plot_map = np.log10(c_map) / np.nanmax(np.log10(c_map))

ax = fig.add_subplot(1, 1, 1, aspect="equal")
im = ax.pcolormesh(
    x_plot / 1000, y_plot / 1000, plot_map, cmap="CMRmap", vmin=0.6, vmax=0.95
)
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")

ax.scatter(
    d_obj.station_locations.rel_east / 1000,
    d_obj.station_locations.rel_north / 1000,
    marker="v",
    s=12,
    c="k",
)

ax.set_xlim((-8, 8))
ax.set_ylim((-8, 8))

plt.colorbar(im, ax=ax)

plt.show()
array2raster.array2raster(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\steam_map.tif",
    (-122.96702 + 0.026, 38.732042 + 0.023),
    200,
    200,
    np.log10(c_map),
)
