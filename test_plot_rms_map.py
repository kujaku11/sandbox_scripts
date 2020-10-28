# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 13:42:25 2018

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate
import numpy as np

res_fn = r"c:\\Users\\jpeacock\\Documents\\Geothermal\\Umatilla\\modem_inv\\inv_03\\um_err03_cov03_NLCG_130.res"

prms = modem.PlotRMSMaps(res_fn, plot_yn="n")
# prms.period_index = 15
# prms.plot_map()
prms.plot_loop(style="map", fig_format="pdf")


# d = modem.Data()
# d.read_data_file(res_fn)
#
# lat = d.data_array['lat']
# lon = d.data_array['lon']
# rms_arr = d.data_array['z'][:, 0, 0, 1].__abs__()/d.data_array['z_err'][:, 0, 0, 1].real
#
# x = np.linspace(lon.min(), lon.max(), 100)
# y = np.linspace(lat.min(), lat.max(), 100)
#
# grid_x, grid_y = np.meshgrid(x, y)
#
# points = np.array([lon, lat])
#
# rms_map = interpolate.griddata(points.T,
#                               np.nan_to_num(rms_arr),
#                               (grid_x, grid_y),
#                               method='cubic')
#
# fig = plt.figure(3)
# fig.clf()
# ax = fig.add_subplot(1, 1, 1, aspect='equal')
# im = ax.pcolormesh(grid_x, grid_y, rms_map, cmap='jet', vmin=0, vmax=5)
# plt.colorbar(im, ax=ax, shrink=.6)
# plt.show()
