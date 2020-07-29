# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:49:18 2020

@author: jpeacock
"""

import numpy as np
import pandas as pd
from mtpy.modeling import modem
from matplotlib import pyplot as plt

dfn = r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\MonoLake\inv_03\ml_modem_data_z07.dat"
mfn = r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\MonoLake\inv_03\ml_modem_sm02_topo_lake.rho"
dfn2 = r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\MonoLake\inv_03\ml_modem_data_z03_t02_topography.dat"

d = modem.Data()
d.read_data_file(dfn)

m = modem.Model()
m.read_model_file(mfn)

x = m.grid_north
y = m.grid_east
z = m.grid_z

z_list = []
for s_arr in d.data_array:
    sx = s_arr['rel_north']
    sy = s_arr['rel_east']
    
    x_find = np.where((sx <= x[1:]) & (sx >= x[:-1]))[0][0]
    y_find = np.where((sy <= y[1:]) & (sy >= y[:-1]))[0][0]
    z_find = np.amin(np.where(m.res_model[x_find, y_find, :] < 1E10)) 
    z_test = np.where(m.res_model[x_find, y_find, :] < 1E10)[0][0]

    z_list.append({'station':s_arr['station'],
                   'grid_north':s_arr['rel_north'],
                   'grid_east':s_arr['rel_east'],
                   'grid_elev':s_arr['rel_elev'],
                   'find_north': x[x_find],
                   'find_east': y[y_find],
                   'find_elev': z[z_find],
                   'diff': s_arr['rel_elev'] - z[z_find],
                   'index_east': y_find,
                   'index_north': x_find,
                   'index_z': z_find})
    
df = pd.DataFrame(z_list)
df.to_csv(r"c:\Users\jpeacock\elevations_test.csv")

# fig = plt.figure(1)
# ax1 = fig.add_subplot(2, 2, 1)
# ax2 = fig.add_subplot(2, 2, 2, sharex=ax1)
# ax3 = fig.add_subplot(2, 2, 3, sharex=ax1, sharey=ax2)

# xg, yg = np.meshgrid(x, y, indexing='ij')
# yzg, zyg = np.meshgrid(y, z, indexing='ij')
# xzg, zxg = np.meshgrid(x, z, indexing='ij')

# ax1.pcolormesh(xg, yg, np.log10(m.res_model[:, :, z_find]), vmin=-1, vmax=3)
# ax2.pcolormesh(xzg, zxg, np.log10(m.res_model[:, y_find, :]), vmin=-1, vmax=3)
# ax3.pcolormesh(yzg, zyg, np.log10(m.res_model[x_find, :, :]), vmin=-1, vmax=3)

# ax1.scatter(sx, sy, marker = 'o', s=30, c='cyan')
# ax2.scatter(sx, elev, marker = 'o', s=30, c='cyan')
# ax3.scatter(sy, elev, marker = 'o', s=30, c='cyan')

# ax1.set_xlabel('Easting')
# ax2.set_xlabel('Easting')
# ax1.set_ylabel('Northing')
# ax3.set_xlabel('Northing')

# ax1.set_xlim((x[x_find-2], x[x_find+2]))
# ax1.set_ylim((y[y_find-2], y[y_find+2]))
# ax2.set_ylim((z.min(), z[z_find+6]))

# ax4 = fig.add_subplot(2, 2, 4)

# plt.colorbar()
# plt.show()
            

