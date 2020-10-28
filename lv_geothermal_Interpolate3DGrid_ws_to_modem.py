# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 14:42:53 2014

@author: jpeacock-pr
"""


import mtpy.modeling.modem_new as modem
import scipy.interpolate as spi
import numpy as np
import time
import matplotlib.pyplot as plt
import mtpy.modeling.ws3dinv as ws

modem_data_fn = (
    r"/home/jpeacock/Documents/ModEM/LV/geo_inv2/lv_geo_err12_tip10_edit.dat"
)

modem_model_fn = r"/home/jpeacock/Documents/ModEM/LV/geo_inv2/sm_lv_big.rho"
ws_model_fn = (
    r"/home/jpeacock/Documents/wsinv3d/LV/geothermal_deep_02/lv_geo_deep_model.03_05"
)
ws_data_fn = r"/home/jpeacock/Documents/wsinv3d/LV/geothermal_deep_02/WS_data_lv_geo_deep_8_deep.dat"
ws_station_fn = (
    r"/home/jpeacock/Documents/wsinv3d/LV/geothermal_deep_02/WS_Station_Locations.txt"
)

# difference between modem and ws grids
# shift_east = 3700
# shift_north = -3700
shift_east = 4500
shift_north = 1700

modem_data = modem.Data()
modem_data.read_data_file(modem_data_fn)

modem_mod = modem.Model()
modem_mod.read_model_file(modem_model_fn)


ws_mod = ws.WSModel(ws_model_fn)
ws_mod.read_model_file()

ws_data = ws.WSData()
ws_data.read_data_file(data_fn=ws_data_fn, station_fn=ws_station_fn)


print "Start Time = {0}".format(time.ctime())

pad = 8
north, east = np.broadcast_arrays(ws_mod.grid_north[:, None], ws_mod.grid_east[None, :])

# 2) do a 2D interpolation for each layer, much faster
new_res = np.zeros(
    (
        modem_mod.grid_north.shape[0],
        modem_mod.grid_east.shape[0],
        modem_mod.grid_z.shape[0],
    )
)

for zz in range(modem_mod.grid_z.shape[0]):
    try:
        old_zz = np.where(ws_mod.grid_z >= modem_mod.grid_z[zz])[0][0]
    except IndexError:
        old_zz = -1

    print "New depth={0:.2f}; old depth={1:.2f}".format(
        modem_mod.grid_z[zz], ws_mod.grid_z[old_zz]
    )

    new_res[:, :, zz] = spi.griddata(
        (north.ravel(), east.ravel()),
        ws_mod.res_model[:, :, old_zz].ravel(),
        (
            modem_mod.grid_north[:, None] + shift_north,
            modem_mod.grid_east[None, :] + shift_east,
        ),
        method="linear",
    )

    new_res[0:pad, pad:-pad, zz] = new_res[pad, pad:-pad, zz]
    new_res[-pad:, pad:-pad, zz] = new_res[-pad - 1, pad:-pad, zz]
    new_res[:, 0:pad, zz] = (
        new_res[:, pad, zz].repeat(pad).reshape(new_res[:, 0:pad, zz].shape)
    )
    new_res[:, -pad:, zz] = (
        new_res[:, -pad - 1, zz].repeat(pad).reshape(new_res[:, -pad:, zz].shape)
    )


#
new_res[np.where(np.nan_to_num(new_res) == 0.0)] = 100.0
modem_mod.write_model_file(
    save_path=r"/home/jpeacock/Documents/ModEM/LV/geo_inv2",
    model_fn_basename="lv_geo_wsdeep_sm.rho",
    res_model=new_res,
)
print "End Time = {0}".format(time.ctime())

mod_plot = modem.ModelManipulator(model_fn=modem_mod.model_fn, data_fn=modem_data_fn)

# omfid = file(ws_mod.initial_fn, 'r')
# mlines = omfid.readlines()
# omfid.close()
#
# mfid = file(ws_mod.initial_fn, 'w')
# mfid.writelines(mlines[0:26])
# for kk in range(ws_mod.grid_z.shape[0]):
#    for jj in range(ws_mod.grid_east.shape[0]):
#        for ii in range(ws_mod.grid_north.shape[0]):
#            res_num = new_res[(ws_mod.grid_north.shape[0]-1)-ii, jj, kk]
#            mfid.write('{0:12.5e}\n'.format(res_num))
# mfid.close()
#
# x, y = np.modgrid(ws_mod.grid_east, ws_mod.grid_north)
# fig = plt.figure(2)
# ax1 = fig.add_subplot(1,2,1, aspect='equal')
# ax1.pcolormod(x, y, np.log10(new_res[:, :, 25]), cmap='jet_r', vmin=-1, vmax=4)
# ax1.scatter(ws_data.data['east'], ws_data.data['north'], marker='v', c='k')
#
# ax2 = fig.add_subplot(1, 2, 2, aspect='equal')
# mx, my = np.modgrid(modem_mod.grid_east, modem_mod.grid_north)
# ax2.pcolormod(mx, my, np.log10(modem_mod.res_model[:, :, 27]),
#               cmap='jet_r', vmin=-1, vmax=4)
# ax2.scatter(modem_data.data_array['rel_east'], modem_data.data_array['rel_north'],
#            marker='v', c='k')
#
# for ax in [ax1, ax2]:
#    ax.set_ylim(-20000, 20000)
#    ax.set_xlim(-20000, 20000)
# plt.show()
