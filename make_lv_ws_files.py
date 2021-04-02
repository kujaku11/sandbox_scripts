# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 12:55:59 2014

@author: jpeacock
"""

import mtpy.modeling.ws3dinv as ws
import os

save_path = r"/home/jpeacock/Documents/wsinv3d/LV"
if not os.path.isdir(save_path):
    os.mkdir(save_path)

inv_periods = [0.05, 0.5, 2, 8, 16, 64, 256]

# station_list = [25, 34, 89, 90, 93, 115, 118, 150, 154, 155, 156, 157, 158,
#                159, 161, 162, 164, 165, 167, 168, 169, 170, 171, 172, 174,
#                175, 176, 177, 177, 178, 179, 180, 181, 182, 188, 189, 190,
#                191, 192, 196, 197, 198, 199, 200, 220, 221, 222, 224, 225,
#                226, 231, 232, 235, 236, 237]

station_list = [
    162,
    164,
    165,
    167,
    168,
    169,
    170,
    171,
    172,
    175,
    176,
    177,
    177,
    178,
    179,
    180,
    181,
    182,
    188,
    189,
    190,
    191,
    192,
    196,
    197,
    198,
    199,
    200,
    220,
    221,
    222,
    224,
    225,
    226,
    231,
    232,
    235,
    236,
    237,
]

lv_list = [21, 20, 14, 15, 17, 19, 1, 4, 3, 13, 9, 6]

edi_path_lv = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files"
edi_path_ps = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files_ps"
edi_path_dp = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files_dp"
edi_path_ga = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files_ga"

edi_list_lv = [os.path.join(edi_path_lv, "LV{0:02}.edi".format(ss)) for ss in lv_list]

edi_list_ps = [
    os.path.join(edi_path_ps, "mb{0:03}_ps.edi".format(ss)) for ss in station_list
]
edi_list_dp = [
    os.path.join(edi_path_dp, "mb{0:03}_dp.edi".format(ss)) for ss in station_list
]
edi_list_ga = [
    os.path.join(edi_path_ga, "mb{0:03}_ga.edi".format(ss)) for ss in station_list
]

# --> make mesh
# ws_mesh = ws.WSMesh(edi_list_ps+edi_list_lv)
# ws_mesh.n_layers = 35
# ws_mesh.pad_z = 3
# ws_mesh.make_mesh()
# ws_mesh.plot_mesh()
# ws_mesh.save_path = save_path
# ws_mesh.write_initial_file(res_list=[100])

ws_mesh = ws.WSMesh()
ws_mesh.read_initial_file(r"/home/jpeacock/Documents/wsinv3d/LV/WSInitialModel_small")
ws_mesh.station_fn = (
    r"/home/jpeacock/Documents/wsinv3d/LV/WS_Station_Locations_small.txt"
)
ws_stations = ws.WSStation()
ws_stations.read_station_file(ws_mesh.station_fn)
ws_mesh.station_locations = ws_stations.station_locations.copy()
ws_mesh.plot_mesh()


# --> make data files
for edi_lst, folder in zip([edi_list_ps, edi_list_ga, edi_list_dp], ["ps", "ga", "dp"]):
    ws_data = ws.WSData(
        edi_list=edi_lst + edi_list_lv,
        period_list=inv_periods,
        station_fn=ws_mesh.station_fn,
    )
    ws_data.n_z = 8
    ws_data.z_err = 0.07
    ws_data.z_err_map = [10, 1, 1, 10]
    ws_data.z_err_floor = 0.07
    sv_path = os.path.join(save_path, "Inv2_{0}".format(folder))
    if not os.path.isdir(sv_path):
        os.mkdir(sv_path)
    ws_data.write_data_file(
        save_path=sv_path, data_basename="WS_data_{0}_8_small.dat".format(folder)
    )

    ws_data_fn = os.path.join(
        save_path, "Inv2_{0}".format(folder), "WS_data_{0}_8_small.dat".format(folder)
    )
    ws_startup = ws.WSStartup(
        data_fn=os.path.basename(ws_data_fn),
        initial_fn=os.path.basename(ws_mesh.initial_fn),
    )
    ws_startup.output_stem = "lv_{0}".format(folder)
    ws_startup.save_path = sv_path
    ws_startup.write_startup_file()
