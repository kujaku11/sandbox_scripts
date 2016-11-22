# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 15:48:52 2015

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import numpy as np
from interpolate_models import interpolate_model_grid

m1_fn = r"/home/jpeacock/Documents/ModEM/LV/geo_err12/lv_geo_err03_cov5_NLCG_065.rho"
m2_fn = r"/home/jpeacock/Documents/ModEM/LV/lv_geo_sm_wsdeep_01/lv_geo_ws_err03_cov5_NLCG_118.rho"
m3_fn = r"

#m1_interp_fn = interpolate_model_grid(m1_fn, m2_fn, pad=3, shift_north=5500,
#                                      shift_east=700)
#m1_interp_fn = interpolate_model_grid(m1_fn, m2_fn, pad=3)

m1_obj = modem.Model()
m1_obj.read_model_file(m1_fn)

m2_obj = modem.Model()
m2_obj.read_model_file(m2_fn)

res_avg = np.sqrt(m1_obj.res_model*m2_obj.res_model)

m2_obj.res_model = res_avg
m2_obj.write_model_file(model_fn_basename='lv_geo_sm_avg_02.rho')

mm = modem.ModelManipulator(model_fn=m2_obj.model_fn, 
                            data_fn=r"/home/jpeacock/Documents/ModEM/LV/geo_err12/lv_geo_err12_tip10.dat")