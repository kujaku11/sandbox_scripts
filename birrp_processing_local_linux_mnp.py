# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 12:32:29 2016

@author: jpeacock
"""

import os
import shutil
import mtpy.usgs.zen_processing as zp

# ==============================================================================
# local parameters
# ==============================================================================
coil_calibration_path = r"/mnt/hgfs/MT/birrp_calibrations"
birrp_path = r"/home/peacock/Documents/birrp52/SourceCode/birrp52_big"
local_path = r"/mnt/hgfs/MT/MNP2019"
copy_edi_path = os.path.join(local_path, "EDI_Files_birrp")

if not os.path.exists(copy_edi_path):
    os.mkdir(copy_edi_path)

# ==============================================================================
# Station to process and remote reference
# ==============================================================================
station = "mnp172"
rr_station = ["mnp151", "mnp162", "mnp128"]
# rr_station = None

block_dict = {4096: [0, 1, 2], 256: [1, 2], 4: [0]}

use_df_list = [4]
df_fn = r"/mnt/hgfs/MT/MNP2019/mnp172/mnp172_processing_df.csv"
overwrite = False


local_station_path = os.path.join(local_path, station)
if rr_station is not None:
    if isinstance(rr_station, list):
        rr_local_station_path = []
        for rr in rr_station:
            rr_local_station_path.append(os.path.join(local_path, rr))
    else:
        rr_local_station_path = os.path.join(local_path, rr_station)
    ilev = 1
else:
    rr_local_station_path = None
    ilev = 0

# ==============================================================================
# Process data
# ==============================================================================

b_param_dict = {
    "ilev": ilev,
    "c2threshb": 0.35,
    "c2threshe": 0.35,
    "c2thresh1": 0.35,
    "ainuin": 0.95,
    "ainlin": 0.05,
    "nar": 11,
    "tbw": 2,
}

kwargs_dict = {
    "calibration_list": [
        "2254",
        "2264",
        "2274",
        "2284",
        "2294",
        "2304",
        "2314",
        "2324",
        "2334",
        "2344",
        "2844",
        "2854",
        "3214",
    ],
    "_max_nread": 25000000,
}

zp_obj = zp.Z3D2EDI(
    station_z3d_dir=local_station_path,
    rr_station_z3d_dir=rr_local_station_path,
    station_ts_dir=os.path.join(local_station_path, "TS"),
)
zp_obj.birrp_exe = birrp_path
zp_obj.calibration_path = coil_calibration_path

plot_obj, comb_edi_fn, zdf = zp_obj.process_data(
    df_fn=df_fn,
    df_list=use_df_list,
    notch_dict={4096: None, 256: None, 4: None},
    sr_dict={4096: (1000.0, 25), 256: (24.999, 0.1), 4: (0.1, 0.00001)},
    use_blocks_dict=block_dict,
    birrp_param_dict=b_param_dict,
    overwrite=overwrite,
    **kwargs_dict
)

# cp_edi_fn = os.path.join(copy_edi_path, station+'.edi')
# shutil.copy(comb_edi_fn, cp_edi_fn)
# print('--> Copied {0} to {1}'.format(comb_edi_fn, cp_edi_fn))
