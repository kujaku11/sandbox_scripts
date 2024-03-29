# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 12:32:29 2016

@author: jpeacock
"""

import os
import shutil
from pathlib import Path
import mtpy.usgs.zen_processing as zp
import pandas as pd

# ==============================================================================
# local parameters
# ==============================================================================
coil_calibration_path = r"/mnt/hgfs/MT_Data/birrp_responses"
birrp_path = r"/home/peacock/Documents/birrp52/SourceCode/birrp52_big"
local_path = Path(r"/mnt/hgfs/MT_Data/BV2023")
copy_edi_path = local_path.joinpath("EDI_Files_birrp")
processing_csv = r"/mnt/hgfs/MT_Data/BV2023/processing_loop.csv"
skip_stations = []

if not copy_edi_path.exists():
    os.mkdir(copy_edi_path)
# ==============================================================================
# Station to process and remote reference
# ==============================================================================
df_converter = {
    "rr_station": lambda x: x[1:-1].replace("'", "").split(","),
    "block_4096": lambda x: x[1:-1].replace("'", "").split(","),
    "block_256": lambda x: x[1:-1].replace("'", "").split(","),
    "block_4": lambda x: x[1:-1].replace("'", "").split(","),
}
loop_df = pd.read_csv(processing_csv, converters=df_converter)

# for loop in list(loop_df.itertuples())[[17, 27, 28, 29, 30]]:
for loop in loop_df.iloc[0:].itertuples():
    station = f"bv{loop.station}"
    if station in skip_stations:
        continue
    # if station not in process_stations:
    #     continue

    rr_station = [f"bv{ss.strip()}" for ss in loop.rr_station]

    block_dict = {
        4096: [int(ss.strip()) for ss in loop.block_4096],
        256: [int(ss.strip()) for ss in loop.block_256],
        4: [int(ss.strip()) for ss in loop.block_4],
    }

    use_df_list = [4096, 256, 4]
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
        "ainuin": 0.9999,
        "ainlin": 0.0000,
        "nar": 7,
        "tbw": 2,
    }

    zp_obj = zp.Z3D2EDI(
        station_z3d_dir=local_station_path,
        rr_station_z3d_dir=rr_local_station_path,
        station_ts_dir=os.path.join(local_station_path, "TS"),
    )
    zp_obj.birrp_exe = birrp_path
    zp_obj.calibration_path = coil_calibration_path
    kw_dict = {
        "df_list": use_df_list,
        "notch_dict": {4096: None, 256: None, 4: None},
        "sr_dict": {4096: (1000.0, 24.9), 256: (24.899, 0.01), 4: (0.01, 0.00001)},
        "use_blocks_dict": block_dict,
        "birrp_param_dict": b_param_dict,
        "overwrite": overwrite,
    }

    with zp.Capturing() as output:
        try:
            plot_obj, comb_edi_fn = zp_obj.process_data(**kw_dict)
            cp_edi_fn = os.path.join(copy_edi_path, station + ".edi")
            shutil.copy(comb_edi_fn, cp_edi_fn)
            plot_obj.fig.savefig(
                os.path.join(copy_edi_path, "{0}.png".format(station)), dpi=300
            )
            print("--> Copied {0} to {1}".format(comb_edi_fn, cp_edi_fn))
            plot_obj.fig.clf()
        except Exception as error:
            print("WARNING: Skipping {0}, rr = {1}".format(station, rr_station))
            print("x" * 50)
            print("ERROR: {0}".format(error))
            print("x" * 50)
    log_fn = os.path.join(local_path, "{0}_processing.log".format(station))
    with open(log_fn, "a") as log_fid:
        log_fid.write("\n".join(output))
