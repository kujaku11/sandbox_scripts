# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 12:55:59 2014

@author: jpeacock
"""

import mtpy.modeling.ws3dinv as ws
import os
import numpy as np

# save_path = r"/home/jpeacock/Documents/wsinv3d/torc/inv_01"
save_path = r"c:\Users\jpeacock\Documents\Geothermal\TorC\inv_ws"
if not os.path.isdir(save_path):
    os.mkdir(save_path)

inv_periods = np.logspace(np.log10(0.05), np.log10(256), 8)

# edi_path = r"/mnt/hgfs/jpeacock/Documents/Geothermal/TorC/EDI_Files_INV"
edi_path = r"c:\Users\jpeacock\Documents\Geothermal\TorC\EDI_Files_INV"
edi_list = [
    os.path.join(edi_path, edi) for edi in os.listdir(edi_path) if edi.endswith(".edi")
]

# --> make mesh
ws_mesh = ws.WSMesh(edi_list)
ws_mesh.save_path = save_path
ws_mesh.n_layers = 35
ws_mesh.pad_z = 4
ws_mesh.cell_size_east = 300
ws_mesh.cell_size_north = 300
ws_mesh.make_mesh()
ws_mesh.plot_mesh()

ws_mesh.write_initial_file(res_list=[50])

# --> make data files
ws_data = ws.WSData(
    edi_list=edi_list, period_list=inv_periods, station_fn=ws_mesh.station_fn
)
ws_data.n_z = 8
ws_data.z_err = 0.05
ws_data.z_err_map = [10, 1, 1, 10]
ws_data.z_err_floor = 0.05
ws_data.write_data_file(save_path=save_path, data_basename="WS_torc_data_err05.dat")

ws_startup = ws.WSStartup(
    data_fn=os.path.basename(ws_data.data_fn),
    initial_fn=os.path.basename(ws_mesh.initial_fn),
)
ws_startup.output_stem = "torc"
ws_startup.save_path = save_path
ws_startup.write_startup_file()
