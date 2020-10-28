# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 10:37:15 2015

@author: jpeacock
"""

import mtpy.modeling.ws3dinv as ws
import matplotlib.pyplot as plt
import os
import numpy as np

model1_fn = (
    r"/home/jpeacock/Documents/wsinv3d/LV/sm_modem_inv1/lv_sm_modem_inv1_fine_model.03"
)
model2_fn = (
    r"/home/jpeacock/Documents/wsinv3d/LV/sm_modem_inv2/lv_sm_modem_inv2_fine_model.07"
)

dfn = r"/home/jpeacock/Documents/wsinv3d/LV/sm_modem_inv2/WS_data_sm_modem_inv1_8_small.dat"
sfn = r"/home/jpeacock/Documents/wsinv3d/LV/WS_Station_Locations.txt"

ws_data = ws.WSData()
ws_data.read_data_file(data_fn=dfn, station_fn=sfn)

m1 = ws.WSModel(model1_fn)
m2 = ws.WSModel(model2_fn)

new_model = np.sqrt(m1.res_model * m2.res_model)

omfid = file(m1.model_fn, "r")
mlines = omfid.readlines()
omfid.close()

mfid = file(r"/home/jpeacock/Documents/wsinv3d/LV/lv_sm_avg.ws", "w")
mfid.writelines(mlines[0:26])
for kk in range(m1.grid_z.shape[0]):
    for jj in range(m1.grid_east.shape[0]):
        for ii in range(m1.grid_north.shape[0]):
            res_num = new_model[(m1.grid_north.shape[0] - 1) - ii, jj, kk]
            mfid.write("{0:12.5e}\n".format(res_num))
mfid.close()

fig = plt.figure(1)
x, y = np.meshgrid(m1.grid_east, m1.grid_north)
ax1 = fig.add_subplot(1, 3, 1, aspect="equal")
p1 = ax1.pcolormesh(
    x, y, np.log10(m1.res_model[:, :, 29]), cmap="jet_r", vmin=-1, vmax=4
)
ax2 = fig.add_subplot(1, 3, 2, aspect="equal")
p1 = ax2.pcolormesh(
    x, y, np.log10(m2.res_model[:, :, 29]), cmap="jet_r", vmin=-1, vmax=4
)
ax3 = fig.add_subplot(1, 3, 3, aspect="equal")
p1 = ax3.pcolormesh(x, y, np.log10(new_model[:, :, 29]), cmap="jet_r", vmin=-1, vmax=4)
# plt.colorbar(p1)

plt.show()
