# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:02:57 2015

@author: jpeacock
"""

import mtpy.modeling.ws3dinv as ws
import os
import numpy as np

edi_path = r"/mnt/hgfs/Google Drive-2/Mono_Basin/INV_EDI_FILES"
save_path = r"/home/jpeacock/Documents/wsinv3d/LV/geothermal_shallow"
# inv_periods = np.array([1, 3, 7, 10, 30, 70, 100, 300])
inv_periods = np.array([0.01, 0.1, 0.3, 1, 3, 10, 30, 100])

if not os.path.isdir(save_path):
    os.mkdir(save_path)

station_list = [
    "mb{0:03}".format(ii)
    for ii in [
        178,
        177,
        220,
        176,
        222,
        221,
        175,
        225,
        188,
        235,
        236,
        237,
        190,
        226,
        179,
        180,
        181,
        231,
        189,
        237,
        232,
        191,
        192,
        182,
        197,
        198,
        196,
        199,
        200,
        300,
        301,
        302,
        303,
        315,
        316,
        317,
        318,
        306,
        307,
        308,
        309,
        311,
        339,
        320,
        305,
        323,
        326,
    ]
]
pw_station_list = [
    "lv{0:02}".format(ii) for ii in [22, 21, 20, 14, 16, 17, 18, 19, 12, 2, 13, 10, 9]
]

edi_list = [
    os.path.join(edi_path, "{0}.edi".format(ss))
    for ss in station_list + pw_station_list
]


# --> make mesh
ws_mesh = ws.WSMesh(edi_list)
ws_mesh.save_path = save_path
ws_mesh.cell_size_east = 500.0
ws_mesh.cell_size_north = 500.0
ws_mesh.n_layers = 35
ws_mesh.pad_z = 3
ws_mesh.pad_east = 8
ws_mesh.pad_north = 8
ws_mesh.pad_root_east = 6
ws_mesh.pad_root_north = 6
ws_mesh.z1_layer = 10
ws_mesh.z_target_depth = 30000
ws_mesh.res_list = [500]
ws_mesh.make_mesh()
ws_mesh.plot_mesh()
ws_mesh.write_initial_file(
    initial_fn=os.path.join(save_path, "WSInitialMesh500m_shallow"), res_list=[30]
)


# --> make data files
folder = "lv_geo_shallow"
ws_data = ws.WSData(
    edi_list=edi_list, period_list=inv_periods, station_fn=ws_mesh.station_fn
)
ws_data.n_z = 8
ws_data.z_err = 0.12
ws_data.z_err_map = [5, 1, 1, 5]
sv_path = save_path
if not os.path.isdir(sv_path):
    os.mkdir(sv_path)
ws_data.write_data_file(
    save_path=save_path, data_basename="WS_data_{0}_8_shallow.dat".format(folder)
)

ws_startup = ws.WSStartup(
    data_fn=os.path.basename(ws_data.data_fn),
    initial_fn=os.path.basename(ws_mesh.initial_fn),
)
ws_startup.output_stem = "{0}".format(folder)
ws_startup.save_path = sv_path
ws_startup.write_startup_file()
