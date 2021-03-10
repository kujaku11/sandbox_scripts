# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 18:11:42 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
import numpy as np
from matplotlib import pyplot as plt
from mtpy.modeling import modem
from mtpy.utils import array2raster

mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_topo_inv_02\st_z05_t02_c025_126.rho"

z_min = 12000
z_max = 40000
pad = 7

m = modem.Model()
m.read_model_file(mfn)

index_min = np.where(m.grid_z <= z_min)[0][-1]
index_max = np.where(m.grid_z >= z_max)[0][0]

conductance = (1./m.res_model[:, :, index_min:index_max].sum(
    axis=2)) * (z_max - z_min) * 750 **2

gx, gy = np.meshgrid(m.grid_east, m.grid_north)

fig = plt.figure(1)
fig.clf()
ax = fig.add_subplot(1, 1, 1, aspect="equal")
im = ax.pcolormesh(gx, gy,
                   conductance, 
                   cmap="hot", 
                   vmin=conductance[pad:-pad, pad:-pad].min(),
                   vmax=conductance[pad:-pad, pad:-pad].max())

ax.set_xlim((m.grid_east[pad], m.grid_east[-pad]))
ax.set_ylim((m.grid_north[pad], m.grid_north[-pad]))

cb = plt.colorbar(im, ax=ax)

plt.show()

array2raster.array2raster(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\st_figures\conductance_lower_crust.tiff",
                          (-118.590929, 38.541344000000002),
                          750.,
                          750.,
                          conductance[pad:-pad, pad:-pad])
