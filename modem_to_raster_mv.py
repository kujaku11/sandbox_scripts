# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:37:19 2015

@author: jpeacock-pr
"""

import mtpy.utils.array2raster as a2r
import os

#model_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\modem_inv\mb_rot_tip02_cov03_NLCG_083.rho"
model_fn = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\modem_inv\inv_03\um_err03_cov03_NLCG_130.rho"


save_path = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\modem_inv\inv_03\depth_slices"
model_center = (-118.534252, 45.647057)

def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print 'Made directory {0}'.format(directory_path)
        
check_dir(save_path)

modem_raster = a2r.ModEM_to_Raster()
modem_raster.model_fn = model_fn
ll_cc = modem_raster.get_model_lower_left_coord(model_center=model_center,
                                                pad_east=5, pad_north=5)
modem_raster.lower_left_corner = (ll_cc[0]+0.01, ll_cc[1]-0.000)
modem_raster.save_path = save_path
modem_raster.projection = 'WGS84'
modem_raster.rotation_angle = 0.0
modem_raster.write_raster_files()