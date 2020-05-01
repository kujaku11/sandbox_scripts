# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:37:19 2015

@author: jpeacock-pr
"""

import mtpy.utils.array2raster as a2r
import os

#model_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\modem_inv\mb_rot_tip02_cov03_NLCG_083.rho"
#model_fn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_02\mp_rr10_cov03_NLCG_106.rho"
model_fn = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\modem_inv\inv_07\mp_z03_c03_159.rho"
save_path = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\modem_inv\inv_07\depth_slices_z03_c03_159.rho"

#model_center = (-115.503979, 35.481154)
#model_center = (-115.503989, 35.481191)
model_center = (-115.504000, 35.481000)
ll_cc = (-115.78898, 35.37412)
 

def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print('Made directory {0}'.format(directory_path))
        
check_dir(save_path)

modem_raster = a2r.ModEM_to_Raster()
modem_raster.model_fn = model_fn
# ll_cc = modem_raster.get_model_lower_left_coord(model_center=model_center,
#                                                 pad_east=6, pad_north=6)
modem_raster.lower_left_corner = (ll_cc[0]+.0608, ll_cc[1]+.04733)
modem_raster.save_path = save_path
modem_raster.projection = 'WGS84'
modem_raster.rotation_angle = 0.0
modem_raster.write_raster_files(pad_east=7, pad_north=7)