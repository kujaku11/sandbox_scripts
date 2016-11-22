# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 12:55:59 2014

@author: jpeacock
"""

import mtpy.modeling.ws3dinv as ws
import os
import numpy as np

save_path = r"/home/jpeacock/Documents/wsinv3d/MountainPass"
if not os.path.isdir(save_path):
    os.mkdir(save_path)

folder = 2

sv_path = os.path.join(save_path, 'Inv{0:02}'.format(folder))
if not os.path.isdir(sv_path):
    os.mkdir(sv_path)

    
inv_periods = np.array([.05, .3, .7, 3, 7, 16, 64, 128])

station_list = ['mp{0:02}'.format(ii) for ii in range(1, 20)]
station_list.remove('mp06')

edi_path_dp = r"/mnt/hgfs/MTData/MountainPass/EDI_INV_FILES"

edi_list_dp = [os.path.join(edi_path_dp, '{0}.edi'.format(ss))
               for ss in station_list]


#--> make mesh
ws_mesh = ws.WSMesh(edi_list_dp) 
ws_mesh.n_layers = 35
ws_mesh.pad_z = 3
ws_mesh.cell_size_east = 600
ws_mesh.cell_size_north = 600
ws_mesh.pad_root_east = 6
ws_mesh.pad_root_north = 6
ws_mesh.pad_east = 7
ws_mesh.pad_north = 7
ws_mesh.make_mesh()
ws_mesh.plot_mesh()
ws_mesh.save_path = sv_path
ws_mesh.write_initial_file(res_list=[100]) 

#ws_mesh = ws.WSMesh()
#ws_mesh.read_initial_file(r"/home/jpeacock/Documents/wsinv3d/LV/WSInitialModel_small")
#ws_mesh.station_fn = r"/home/jpeacock/Documents/wsinv3d/LV/WS_Station_Locations_small.txt"
#ws_stations = ws.WSStation()
#ws_stations.read_station_file(ws_mesh.station_fn)
#ws_mesh.station_locations = ws_stations.station_locations.copy()
#ws_mesh.plot_mesh()


#--> make data files
#for edi_lst, folder in zip([edi_list_ps, edi_list_ga, edi_list_dp], 
#                           ['ps', 'ga', 'dp']):

ws_data = ws.WSData(edi_list=edi_list_dp, period_list=inv_periods, 
                    station_fn=ws_mesh.station_fn)
ws_data.period_list = inv_periods
ws_data.n_z = 8
#ws_data.z_err = .07
ws_data.z_err_map = [3, 1, 1, 3]
ws_data.z_err_floor = .07

if not os.path.isdir(sv_path):
    os.mkdir(sv_path)
ws_data.write_data_file(save_path=sv_path,
                        data_basename='WS_data_{0:02}_8_small.dat'.format(folder))

ws_data_fn = os.path.join(save_path, 'Inv{0:02}'.format(folder), 
                          'WS_data_{0:02}_8_small.dat'.format(folder)) 
ws_startup = ws.WSStartup(data_fn=os.path.basename(ws_data_fn),
                          initial_fn=os.path.basename(ws_mesh.initial_fn))
ws_startup.output_stem = 'mp_{0:02}'.format(folder)
ws_startup.save_path = sv_path
ws_startup.write_startup_file()

                 
                   
