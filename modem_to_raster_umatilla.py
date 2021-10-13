# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:37:19 2015

@author: jpeacock-pr
"""

import mtpy.utils.array2raster as a2r
import os
import numpy as np

# model_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\modem_inv\mb_rot_tip02_cov03_NLCG_083.rho"
# model_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_06\um_z05_c03_083.rho"
model_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_09\um_z05_c025_086.rho"

# save_path = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_06\depth_slices"
save_path = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_09\depth_slices2"
# model_center = (45.650594, -118.562997)
model_center = (45.654713, -118.547148)
z_dict = {
    "upper_1km": np.array((-300, 700)),
    "1-3km": np.array((700, 4500)),
    "below_3km": np.array((4500, 30000)),
}


def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print("Made directory {0}".format(directory_path))


check_dir(save_path)

modem_raster = a2r.ModEM_to_Raster()
modem_raster.model_fn = model_fn
modem_raster.model_obj = modem_raster._get_model()
ll_cc = modem_raster.get_model_lower_left_coord(
    modem_raster.model_obj, model_center=model_center, pad_east=9, pad_north=9
)
modem_raster.lower_left_corner = (ll_cc[0] + 0.0, ll_cc[1] - 0.000)
modem_raster.save_path = save_path
modem_raster.projection = "WGS84"
modem_raster.rotation_angle = 0.0
# modem_raster.write_conductance_raster_files(z_dict)
modem_raster.write_raster_files()
