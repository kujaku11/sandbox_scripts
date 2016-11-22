# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 12:55:59 2014

@author: jpeacock
"""

import mtpy.modeling.ws3dinv as ws
import os

save_path = r"/home/jpeacock/Documents/wsinv3d/MB_MT/Inv1_dp"
if not os.path.isdir(save_path):
    os.mkdir(save_path)
    
inv_periods = [.05, .5, 2, 8, 16, 64, 256]

station_list = [17, 18, 25, 26, 34, 36, 40, 41, 46, 49, 51, 54, 55, 57, 59,
                60, 63, 64, 65, 67, 68, 69, 70, 71, 72, 73, 74, 75, 89, 90, 91,
                92, 93, 108,  110, 112, 113, 115, 118, 119, 124,
                125, 126, 129, 130, 141, 142, 143, 150, 151, 153, 154, 156,
                157, 158, 159, 161, 21, 133]


edi_path_dp = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files_dp"
#edi_path_ga = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files_ga"

#edi_list_lv = [os.path.join(edi_path_lv, 'LV{0:02}.edi'.format(ss))
#               for ss in lv_list]

#edi_list_ps = [os.path.join(edi_path_ps, 'mb{0:03}_ps.edi'.format(ss))
#               for ss in station_list]
edi_list_dp = [os.path.join(edi_path_dp, 'mb{0:03}_dp.edi'.format(ss))
               for ss in station_list]
#edi_list_ga = [os.path.join(edi_path_ga, 'mb{0:03}_ga.edi'.format(ss))
#               for ss in station_list]

#--> make mesh
ws_mesh = ws.WSMesh(edi_list_dp) 
ws_mesh.n_layers = 30
ws_mesh.pad_z = 3
ws_mesh.make_mesh()
ws_mesh.plot_mesh()
ws_mesh.save_path = save_path
ws_mesh.write_initial_file(res_list=[100]) 

#ws_mesh = ws.WSMesh()
#ws_mesh.read_initial_file(r"/home/jpeacock/Documents/wsinv3d/MB_MT/WSInitialModel_small")
#ws_mesh.station_fn = r"/home/jpeacock/Documents/wsinv3d/LV/WS_Station_Locations_small.txt"
ws_stations = ws.WSStation()
ws_stations.read_station_file(ws_mesh.station_fn)
ws_mesh.station_locations = ws_stations.station_locations.copy()
ws_mesh.plot_mesh()


#--> make data files
#for edi_lst, folder in zip([edi_list_ps, edi_list_ga, edi_list_dp], 
#                           ['ps', 'ga', 'dp']):

ws_data = ws.WSData(edi_list=edi_list_dp, period_list=inv_periods, 
                    station_fn=ws_mesh.station_fn)
ws_data.n_z = 8
ws_data.z_err = .07
ws_data.z_err_map = [10, 1, 1, 10]
ws_data.z_err_floor = .07
sv_path = os.path.join(save_path, 'Inv1_{0}'.format('dp'))
if not os.path.isdir(sv_path):
    os.mkdir(sv_path)
ws_data.write_data_file(save_path=sv_path,
                        data_basename='WS_data_{0}_8_small.dat'.format('dp'))

ws_data_fn = os.path.join(save_path, 'Inv1_{0}'.format('dp'), 
                          'WS_data_{0}_8_small.dat'.format('dp')) 
ws_startup = ws.WSStartup(data_fn=os.path.basename(ws_data_fn),
                          initial_fn=os.path.basename(ws_mesh.initial_fn))
ws_startup.output_stem = 'lv_{0}'.format('dp')
ws_startup.save_path = sv_path
ws_startup.write_startup_file()

                 
                   
