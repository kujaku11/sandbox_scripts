# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 18:47:08 2017

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import mtpy.modeling.modem as modem
import os
import numpy as np

# =============================================================================
# Inputs
# =============================================================================
#dfn = r"c:\Users\jpeacock\Documents\iMush\modem_inv\shz_inv_01\shz_modem_data_err03_tip02.dat"
dfn = r"c:\Users\jpeacock\Documents\SaudiArabia\modem_inv\med_modem_data_z03_t02_edit.dat"

remove_stations = None
shady_stations = ['med133', 'med312']
add_err = 5
elevation_bool = True

inv_modes = ['2']
z_err_value = 5.0
t_err_value = .03
z_err_type = 'eigen_floor'
t_err_type = 'abs_floor'

#sv_fn = os.path.basename(dfn)[0:os.path.basename(dfn).find('_')]
sv_fn = 'med'
# =============================================================================
# change data file
# =============================================================================
d_obj = modem.Data()
d_obj.read_data_file(dfn)

### add error to certain stations
for e_station in shady_stations:
    s_find = np.where(d_obj.data_array['station'] == e_station)[0][0]
    d_obj.data_array[s_find]['z_err'] *= add_err 
    
### remove a bad station
if remove_stations is not None:
    for b_station in remove_stations:
        s_find = np.where(d_obj.data_array['station'] == b_station)[0][0]
        d_obj.data_array[s_find]['z'][:] = 0 
        d_obj.data_array[s_find]['z_err'][:] = 0 
        d_obj.data_array[s_find]['tip'][:] = 0 
        d_obj.data_array[s_find]['tip_err'][:] = 0 
    

for inv_mode in inv_modes:
    d_obj.error_type_z = z_err_type
    d_obj.error_type_tipper = t_err_type
    d_obj.inv_mode = inv_mode
    d_obj.error_value_z = z_err_value
    d_obj.error_value_tipper = t_err_value
    
    
    
    if d_obj.inv_mode == '2':
        d_obj.write_data_file(save_path=os.path.dirname(dfn),
                              fn_basename='{0}_modem_data_z{1:02.0f}.dat'.format(
                                              sv_fn, 
                                              d_obj.error_value_z),
                              fill=False,
                              compute_error=True,
                              elevation=elevation_bool)
    elif d_obj.inv_mode == '5':
        d_obj.write_data_file(save_path=os.path.dirname(dfn),
                              fn_basename='{0}_modem_data_t{1:02.0f}.dat'.format(
                                              sv_fn, 
                                              d_obj.error_value_tipper*100),
                              fill=False,
                              compute_error=True,
                              elevation=elevation_bool)
    else:
        d_obj.write_data_file(save_path=os.path.dirname(dfn),
                              fn_basename='{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat'.format(
                                              sv_fn, 
                                              d_obj.error_value_z,
                                              d_obj.error_value_tipper*100),
                              fill=False,
                              compute_error=True,
                              elevation=elevation_bool)
