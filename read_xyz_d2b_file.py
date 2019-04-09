# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 14:03:32 2019

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt
from mtpy.modeling import modem
from mtpy.utils import gis_tools

fn = r"g:\GabbsValley\DataRelease_PFA\d2b\Grids\Correct_coord_system\GV_d2b_bs_v1.xyz"

a = np.loadtxt(fn, skiprows=1, dtype=np.float)

x = np.unique(a[:, 0])
y = np.unique(a[:, 1])
base = a[:, 2].reshape((y.shape[0], x.shape[0]))

xg, yg = np.meshgrid(x, y)

dfn = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\modem_inv\inv_03\gv_modem_data_z03_t02.dat"
d_obj = modem.Data()
d_obj.read_data_file(dfn)


fig = plt.figure(1)
fig.clf()

ax = fig.add_subplot(1, 1, 1, aspect='equal')
im = ax.pcolormesh(xg, yg, base, cmap='viridis', vmin=0, vmax=2.5)
plt.colorbar(mappable=im, ax=ax)

for lat, lon in zip(d_obj.station_locations.lat, d_obj.station_locations.lon):
    east, north, zone = gis_tools.project_point_ll2utm(lat, lon, epsg=26911)
    ax.scatter(east, north, marker='v', c='k', s=15)


plt.show()
