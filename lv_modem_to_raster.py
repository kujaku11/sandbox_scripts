# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:37:19 2015

@author: jpeacock-pr
"""

import mtpy.utils.array2raster as a2r
import os

# model_fn = r"c:\MinGW32-xy\Peacock\ModEM\LV\sm_avg_inv3_err12_cov5\lv_err12_cov5_NLCG_019.rho"
# model_fn = r"c:\MinGW32-xy\Peacock\ModEM\LV\lv_comb_err03_cov4_NLCG_061.rho\lv_comb_err03_cov4_NLCG_061.rho"
# model_fn = r"c:\MinGW32-xy\Peacock\ModEM\LV\lv_sm_comb_smooth.rho"
# model_fn = r"c:\MinGW32-xy\Peacock\ModEM\LV\Topography_test\lv_elev_err12_cov4_NLCG_053.rho"
# model_fn = r"c:\Users\jpeacock\Documents\LV\Maps\lv_geo_ws_err03_cov5_NLCG_054.rho"
# model_fn = r"c:\Users\jpeacock\Documents\LV\lv_geo_ws_err03_cov5_NLCG_118.rho"
# model_fn = r"c:\Users\jpeacock\Documents\LV\Maps\lv_big_err03_NLCG_122.r1ho"
model_fn = r"c:\Users\jpeacock\Documents\LV\lv16_sm_geo_err05_cov3_NLCG_065.rho"


save_path = r"c:\Users\jpeacock\Documents\LV\Maps\lv16_model_slices_054"
# save_path = r"/mnt/hgfs/jpeacock/Documents/LV/Maps/geo_model_slices_02"
# model_center = (-118.833, 37.815) # lv center
model_center = (-118.833, 37.815)  # lv16 lower left


def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print "Made directory {0}".format(directory_path)


check_dir(save_path)

# ll_cc = (model_center[0]-.860, model_center[1]-.771) # lv ll
ll_cc = (-120.09987536766145 - 0.008, 36.3497971057915 + 0.405)  # lv16 ll

# for big
# ll_cc = (model_center[0]-.895, model_center[1]-.85)

modem_raster = a2r.ModEM_to_Raster()
modem_raster.model_fn = model_fn
modem_raster.lower_left_corner = ll_cc
modem_raster.save_path = save_path
modem_raster.cell_size_east = 500
modem_raster.cell_size_north = 500
modem_raster.pad_east = 1
modem_raster.pad_north = 1
modem_raster.projection = "NAD27"
modem_raster.rotation_angle = 0
modem_raster.write_raster_files()
