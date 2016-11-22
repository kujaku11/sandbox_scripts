# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 17:01:24 2014

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os
import numpy as np

ps_path = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files_dp"
ps_list = [os.path.join(ps_path, edi) for edi in os.listdir(ps_path)
            if edi.find('.edi') > 0]
#--> remove any bad stations
bad_stations = [35, 114, 121, 132, 152]
for bad_station in bad_stations:
    ps_list.remove(os.path.join(ps_path, 'mb{0:03}_dp.edi'.format(bad_station)))
                
lv_path = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files"
lv_list = edi_list = [os.path.join(lv_path, edi) for edi in os.listdir(lv_path)
            if edi.find('.edi') > 0 and edi.find('LV') == 0]
                
edi_list = ps_list+lv_list
save_path = r"/home/jpeacock/Documents/ModEM/LV/Layered1D_Inv1"

if os.path.isdir(save_path) is False:
    os.mkdir(save_path)

#--> make model file first
mesh = modem.Model(edi_list=list(edi_list))
mesh.cell_size_east = 500
mesh.cell_size_north = 500
mesh.n_layers = 40
mesh.pad_east = 20
mesh.pad_north = 20
mesh.pad_z = 5
mesh.pad_stretch_h = 1.5
mesh.pad_stretch_v = 1.3
mesh.z1_layer = 10
mesh.z_target_depth = 40000
mesh.z_bottom = 300000
mesh.make_mesh()
mesh.plot_mesh()
# make a 1d layer model
mesh.res_model = np.zeros((mesh.grid_north.shape[0], 
                           mesh.grid_east.shape[0],
                           mesh.grid_z.shape[0]))
mesh.res_model[:, :, np.where(mesh.grid_z < 2000)] = 50
mesh.res_model[:, :, np.where((mesh.grid_z >= 2000) & (mesh.grid_z <=9000))] = 1000
mesh.res_model[:, :, np.where((mesh.grid_z >= 9000) & (mesh.grid_z <=35000))] = 10
mesh.res_model[:, :, np.where(mesh.grid_z > 35000)] = 50
mesh.write_model_file(save_path=save_path, 
                      model_fn_basename='Layered_starting_model.rho')

#--> make data file
md = modem.Data(edi_list=list(edi_list))
md.error_egbert = 10
md.error_tipper = .07
md.inv_mode = '1'
md.ptol = .15
md.period_list = [.05, .125, .5, 1, 4, 8, 16, 32, 64, 128, 256, 516] 
md.station_locations = mesh.station_locations.copy()
md.write_data_file(save_path=save_path, fn_basename='LV_DP_egbert10.dat')
md.inv_mode = '2'
md.write_data_file(save_path=save_path, fn_basename='LV_DP_egbert10_no_tipper.dat')
md.inv_mode = '5'
md.write_data_file(save_path=save_path, fn_basename='LV_DP_egbert10_tipper.dat')

#--> make control files
cntrl_inv = modem.Control_Inv()
cntrl_inv.write_control_file(save_path=save_path)

cntrl_fwd = modem.Control_Fwd()
cntrl_fwd.write_control_file(save_path=save_path)

#--> make covariance file
cov = modem.Covariance()
cov.grid_dimensions = (mesh.grid_north.shape[0], 
                       mesh.grid_east.shape[0],
                       mesh.grid_z.shape[0])
cov.smoothing_east = 0.5
cov.smoothing_north = 0.5
cov.smoothing_z = 0.5
cov.smoothing_num = 2
cov.write_covariance_file(save_path=save_path)
                