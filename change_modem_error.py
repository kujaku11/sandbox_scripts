# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 18:47:08 2017

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import os

#dfn = r"c:\Users\jpeacock\Documents\iMush\modem_inv\shz_inv_01\shz_modem_data_err03_tip02.dat"
dfn = r"c:\Users\jpeacock\Documents\ShanesBugs\TorC_2018\modem_inv\inv_01\torc_modem_data_err03_tip03_edit.dat"
sv_fn = os.path.basename(dfn)[0:os.path.basename(dfn).find('_')]

d_obj = modem.Data()
d_obj.read_data_file(dfn)

d_obj.error_type_z = 'eigen_floor'
d_obj.error_type_tipper = 'abs_floor'
d_obj.inv_mode = '5'
d_obj.error_value_z = 7.0
d_obj.error_value_tipper = .04


if d_obj.inv_mode == '2':
    d_obj.write_data_file(save_path=os.path.dirname(dfn),
                          fn_basename='{0}_modem_data_ef{1:02.0f}.dat'.format(
                                          sv_fn, 
                                          d_obj.error_value_z),
                          fill=False,
                          compute_error=True,
                          elevation=True)
elif d_obj.inv_mode == '5':
    d_obj.write_data_file(save_path=os.path.dirname(dfn),
                          fn_basename='{0}_modem_data_tip{1:02.0f}.dat'.format(
                                          sv_fn, 
                                          d_obj.error_value_tipper*100),
                          fill=False,
                          compute_error=True,
                          elevation=True)
else:
    d_obj.write_data_file(save_path=os.path.dirname(dfn),
                          fn_basename='{0}_modem_data_ef{1:02.0f}_tip{2:02.0f}.dat'.format(
                                          sv_fn, 
                                          d_obj.error_value_z,
                                          d_obj.error_value_tipper*100),
                          fill=False,
                          compute_error=True,
                          elevation=True)
