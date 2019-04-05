# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:37:19 2015

@author: jpeacock-pr
"""

import mtpy.utils.array2raster as a2r
import os

model_fn = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\modem_inv\inv_02\gv_z03_t03_c02__NLCG_118.rho"
save_path = os.path.join(os.path.dirname(model_fn), "depth_slices")

model_center = (-118.151242, 38.774109)

def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print 'Made directory {0}'.format(directory_path)
        
check_dir(save_path)

modem_raster = a2r.ModEM_to_Raster()
modem_raster.model_fn = model_fn
modem_raster.pad_east = 8
modem_raster.pad_north = 8
modem_raster.lower_left_corner = (model_center[0]-.075, model_center[1]-0.05)
modem_raster.save_path = save_path
modem_raster.projection = 'WGS84'
modem_raster.rotation_angle = 0.0
modem_raster.write_raster_files()