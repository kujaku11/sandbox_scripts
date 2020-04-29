# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:49:18 2020

@author: jpeacock
"""

import numpy as np
from mtpy.modeling import modem
from matplotlib import pyplot as plt

dfn = r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\MonoLake\inv_03\ml_modem_data_z07.dat"
mfn = r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\MonoLake\inv_03\ml_modem_sm02_topo_lake.rho"

d = modem.Data()
d.read_data_file(dfn)

m = modem.Model()
m.read_model_file(mfn)

station ='s53'
s_index = np.where(d.data_array['station'] == station)[0][0]

x = m.grid_north
y = m.grid_east
z = m.grid_z

sx = d.data_array['rel_north'][s_index]
sy = d.data_array['rel_east'][s_index]

x_find = np.where((sx <= x[1:]) & (sx >= x[:-1]))[0][0]
y_find = np.where((sy <= y[1:]) & (sy >= y[:-1]))[0][0]
z_find = np.amin(np.where(m.res_model[x_find, y_find, :] < 20)) 

elev = z[z_find]

fig = plt.figure(1)
ax1 = fig.add_subplot(2, 2, 1)
ax2 = fig.add_subplot(2, 2, 2, sharex=ax1)
ax3 = fig.add_subplot(2, 2, 3, sharex=ax1, sharey=ax2)

xg, yg = np.meshgrid(x, y, indexing='ij')
yzg, zyg = np.meshgrid(y, z, indexing='ij')
xzg, zxg = np.meshgrid(x, z, indexing='ij')

ax1.pcolormesh(xg, yg, np.log10(m.res_model[:, :, z_find]), vmin=-1, vmax=3)
ax2.pcolormesh(xzg, zxg, np.log10(m.res_model[:, y_find, :]), vmin=-1, vmax=3)
ax3.pcolormesh(yzg, zyg, np.log10(m.res_model[x_find, :, :]), vmin=-1, vmax=3)

ax1.scatter(sx, sy, marker = 'o', s=30, c='cyan')
ax2.scatter(sx, elev, marker = 'o', s=30, c='cyan')
ax3.scatter(sy, elev, marker = 'o', s=30, c='cyan')

ax1.set_xlabel('Easting')
ax2.set_xlabel('Easting')
ax1.set_ylabel('Northing')
ax3.set_xlabel('Northing')

ax1.set_xlim((x[x_find-2], x[x_find+2]))
ax1.set_ylim((y[y_find-2], y[y_find+2]))
ax2.set_ylim((z.min(), z[z_find+6]))

ax4 = fig.add_subplot(2, 2, 4)

plt.colorbar()
plt.show()
            

