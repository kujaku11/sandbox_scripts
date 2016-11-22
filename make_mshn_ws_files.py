# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 12:55:59 2014

@author: jpeacock
"""

import mtpy.modeling.ws3dinv as ws
import os

save_path = r"/home/jpeacock/Documents/wsinv3d/MSHN/inv_01"
if not os.path.isdir(save_path):
    os.mkdir(save_path)
    
inv_periods = [.05, .25, 1, 5, 24, 110, 500]

edi_path = r"/mnt/hgfs/jpeacock/Documents/Geothermal/Washington/MSH/INV_EDI_Files"
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi')]

#--> make mesh
ws_mesh = ws.WSMesh(edi_list)
ws_mesh.save_path = save_path 
ws_mesh.n_layers = 35
ws_mesh.pad_z = 4
ws_mesh.z1_layer = 10
ws_mesh.z_target_depth = 30000
ws_mesh.z_bottom = 200000
ws_mesh.cell_size_east = 300
ws_mesh.cell_size_north = 300
ws_mesh.pad_east = 7
ws_mesh.pad_north = 7
ws_mesh.pad_root_east = 7
ws_mesh.pad_root_north = 7
ws_mesh.make_mesh()
ws_mesh.plot_mesh()

#ws_mesh.write_initial_file(res_list=[500]) 
#
##--> make data files
#ws_data = ws.WSData(edi_list=edi_list, 
#                    period_list=inv_periods, 
#                    station_fn=ws_mesh.station_fn)
#ws_data.n_z = 8
#ws_data.z_err = .05
#ws_data.z_err_map = [10, 1, 1, 10]
#ws_data.z_err_floor = .12
#ws_data.write_data_file(save_path=save_path,
#                        data_basename='WS_mshn_data_err12.dat')
#
#ws_startup = ws.WSStartup(data_fn=os.path.basename(ws_data.data_fn),
#                          initial_fn=os.path.basename(ws_mesh.initial_fn))
#ws_startup.output_stem = 'mshn'
#ws_startup.save_path = save_path
#ws_startup.write_startup_file()

                 
                   
