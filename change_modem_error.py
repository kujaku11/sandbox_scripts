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
dfn = r"c:\Users\jpeacock\Documents\MonoBasin\modem_inv\inv_02\ml_modem_data_z05_t02_edit.dat"

#remove_stations = ['MB132', 'MB107']
#shady_stations = None
#remove_x = ['MB510']
#remove_y = ['MB021', 'MB121', 'MB151', 'MB152', 'MB159']
#flip_phase_x = ['B8']
#flip_phase_y = ['B8']
remove_stations = None
shady_stations = None
remove_x = ['MB133']
remove_y = None
flip_phase_x = None
flip_phase_y = None
add_err = 5
elevation_bool = True

inv_modes = ['1']
z_err_value = 5.0
t_err_value = .02
z_err_type = 'eigen_floor'
t_err_type = 'abs_floor'

#sv_fn = os.path.basename(dfn)[0:os.path.basename(dfn).find('_')]
sv_fn = 'ml'
# =============================================================================
# change data file
# =============================================================================
d_obj = modem.Data()
d_obj.read_data_file(dfn)

### add error to certain stations   
if shady_stations is not None:
    for e_station in shady_stations:
        s_find = np.where(d_obj.data_array['station'] == e_station)[0][0]
        d_obj.data_array[s_find]['z_err'] *= add_err 
        d_obj.data_array[s_find]['tip_err'] *= add_err 
    
### remove a bad station
if remove_stations is not None:
    for b_station in remove_stations:
        s_find = np.where(d_obj.data_array['station'] == b_station)[0][0]
        d_obj.data_array[s_find]['z'][:] = 0 
        d_obj.data_array[s_find]['z_err'][:] = 0 
        d_obj.data_array[s_find]['tip'][:] = 0 
        d_obj.data_array[s_find]['tip_err'][:] = 0 

### remove x component
if remove_x is not None:
    for b_station in remove_x:
        s_find = np.where(d_obj.data_array['station'] == b_station)[0][0]
        d_obj.data_array[s_find]['z'][:, 0, :] = 0 
        d_obj.data_array[s_find]['z_err'][:, 0, :] = 0
        
### remove y component
if remove_y is not None:
    for b_station in remove_y:
        s_find = np.where(d_obj.data_array['station'] == b_station)[0][0]
        d_obj.data_array[s_find]['z'][:, 1, :] = 0 
        d_obj.data_array[s_find]['z_err'][:, 1, :] = 0

### flip x phase
if flip_phase_x is not None:
    for b_station in flip_phase_x:
        s_find = np.where(d_obj.data_array['station'] == b_station)[0][0]
        d_obj.data_array[s_find]['z'][:, 0, :] *= -1 
        
### flip x phase
if flip_phase_y is not None:
    for b_station in flip_phase_y:
        s_find = np.where(d_obj.data_array['station'] == b_station)[0][0]
        d_obj.data_array[s_find]['z'][:, 1, :] *= -1 
    

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
