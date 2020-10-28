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

data_fn = r"/mnt/hgfs/ModEM/LV/Topography_test/lv_dp_23p_tip05_elev.dat"

elev_model_fn = r"/mnt/hgfs/ModEM/LV/Topography_test/lv_elev_err12_cov4_NLCG_053.rho"
avg_model_fn = r"/home/jpeacock/Documents/ModEM/LV/sm_comb_err03_inv2/lv_comb_err03_cov4_NLCG_061.rho"

avg_elev_index = 66

elev_mod = modem.Model()
elev_mod.read_model_file(elev_model_fn)

avg_mod = modem.Model()
avg_mod.read_model_file(avg_model_fn)

data_obj = modem.Data()
data_obj.read_data_file(data_fn)

avg_elev = elev_mod.grid_z[avg_elev_index]

elev_res = np.zeros_like(elev_mod.res_model)

avg_north, avg_east = np.broadcast_arrays(
    avg_mod.grid_north[:, None], avg_mod.grid_east[None, :]
)
elev_north, elev_east = np.broadcast_arrays(
    elev_mod.grid_north[:, None], elev_mod.grid_east[None, :]
)
# interpolate the avg grid onto elevation model
# assuming mono lake is 0 elevation
for zz in range(elev_mod.grid_z.shape[0]):
    try:
        avg_zz = np.where(avg_mod.grid_z >= elev_mod.grid_z[zz] - avg_elev)[0][0]
    except IndexError:
        avg_zz = -1

    print "New depth={0:.2f}; elev depth={1:.2f}".format(
        avg_mod.grid_z[avg_zz], elev_mod.grid_z[zz]
    )

    elev_res[:, :, zz] = avg_mod.res_model[:, :, avg_zz]

#    elev_res[:, :, zz] = spi.griddata((avg_north.ravel(), mb_east.ravel()),
#                                    mb_mod.res_model[:, :, mb_zz].ravel(),
#                                   (comb_mod.grid_north[:, None]+comb_center[1],
#                                    comb_mod.grid_east[None, :]+comb_center[0]),
#                                    method='linear')
#
#
#
#    #make the surrounding nan to seem like a half space
#    mb_res[0:mb_left, mb_bottom:mb_top, zz] = mb_res[mb_left, mb_bottom:mb_top, zz]
#    mb_res[mb_right:, mb_bottom:mb_top, zz] = mb_res[mb_right-1, mb_bottom:mb_top, zz]
#    mb_res[:, 0:mb_bottom, zz] = mb_res[:, mb_bottom, zz].repeat(mb_bottom).reshape(
#                                                  mb_res[:, 0:mb_bottom, zz].shape)
#    mb_res[:, mb_top:, zz] = mb_res[:, mb_top-1, zz].repeat(ny-mb_top).reshape(
#                                                  mb_res[:, mb_top:, zz].shape)

elev_res[np.where(elev_mod.res_model > 1e11)] = 1e12


elev_mod.res_model = elev_res
elev_mod.write_model_file(
    save_path=r"/mnt/hgfs/ModEM/LV", model_fn_basename="lv_sm_topo_avg.rho"
)
