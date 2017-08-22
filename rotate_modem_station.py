# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 16:16:20 2017

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import numpy as np

dfn = r"C:\Users\jpeacock\Documents\iMush\modem_inv\station_0911.dat"

d_obj = modem.Data()
d_obj.read_data_file(dfn)

for ii, z in enumerate(d_obj.data_array[0]['z']):
    d_obj.data_array[0]['z'][ii, :, :] = -1*np.fliplr(np.flipud(z))
    
for ii, z_err in enumerate(d_obj.data_array[0]['z_err']):
    d_obj.data_array[0]['z_err'][ii, :, :] = 1*np.fliplr(np.flipud(z_err))
    
for ii, tip in enumerate(d_obj.data_array[0]['tip']):
    d_obj.data_array[0]['tip'][ii, :, :] = np.fliplr(np.flipud(tip))
    
for ii, tip_err in enumerate(d_obj.data_array[0]['tip_err']):
    d_obj.data_array[0]['tip_err'][ii, :, :] = 1*np.fliplr(np.flipud(tip_err))
    
d_obj.write_data_file(fn_basename='station_0911_rot.dat', compute_error=False, 
                      fill=False)
