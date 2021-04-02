# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 11:54:57 2015

@author: jpeacock-pr
"""

import mtpy.modeling.modem_new as modem
import mtpy.analysis.niblettbostick as nb
import numpy as np

# dfn = r"c:\MinGW32-xy\Peacock\ModEM\LV\Topography_test\lv_dp_23p_err12_tip2_elev.dat"
dfn = r"/mnt/hgfs/ModEM/LV/Topography_test/lv_dp_23p_err12_tip2_elev.dat"

d_obj = modem.Data()
d_obj.read_data_file(dfn)

# log_fid = file(r"c:\MinGW32-xy\Peacock\ModEM\LV\Topography_test\depths.log", 'w')
log_fid = file(r"/mnt/hgfs/ModEM/LV/Topography_test/depths.log", "w")

depth_arr_min = np.zeros((d_obj.period_list.shape[0], len(d_obj.mt_dict.keys())))
depth_arr_max = np.zeros((d_obj.period_list.shape[0], len(d_obj.mt_dict.keys())))

for ii, mt_key in enumerate(sorted(d_obj.mt_dict.keys())):
    mt_obj = d_obj.mt_dict[mt_key]
    d_arr = nb.calculate_depth_nb(z_object=mt_obj.Z)
    log_fid.write("-" * 30 + "\n")
    log_fid.write("{0}\n".format(mt_key))
    log_fid.write("-" * 30 + "\n")
    for jj, dd in enumerate(d_arr):
        log_fid.write(
            "{0:<10.5g}{1:<10.2f}{2:<10.2f}\n".format(
                dd["period"], dd["depth_min"], dd["depth_max"]
            )
        )
    depth_arr_min[:, ii] = d_arr["depth_min"]
    depth_arr_max[:, ii] = d_arr["depth_max"]

log_fid.close()

depth_avg_min = np.array(
    [
        depth_arr_min[kk, np.nonzero(depth_arr_min[kk, :])].mean()
        for kk in range(d_obj.period_list.shape[0])
    ]
)
depth_avg_max = np.array(
    [
        depth_arr_max[kk, np.nonzero(depth_arr_max[kk, :])].mean()
        for kk in range(d_obj.period_list.shape[0])
    ]
)

depth_avg = (depth_avg_min + depth_avg_max) / 2
