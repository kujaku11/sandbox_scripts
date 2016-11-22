# -*- coding: utf-8 -*-
"""
Created on Thu Nov 06 13:01:16 2014

@author: jpeacock-pr
"""

import mtpy.utils.array2raster as a2r

model_fn = r"c:\MinGW32-xy\Peacock\ModEM\Inv3\mb_NLCG_058.rho"

model_center = (-118.933, 37.866)

#ll_cc = (model_center[0]-.4255, model_center[1]-.2725)
#for rotation
ll_cc = (model_center[0]-.345, model_center[1]-.3435)

modem_raster = a2r.ModEM_to_Raster()
modem_raster.model_fn = model_fn
modem_raster.lower_left_corner = ll_cc
modem_raster.save_path = r"c:\Users\jpeacock-pr\Google Drive\Mono_Basin\Models\GIS_depth_slices_rotate"
modem_raster.pad_east = 7
modem_raster.pad_north = 7
modem_raster.projection = 'NAD27'
modem_raster.rotation_angle = 13.37
modem_raster.write_raster_files()