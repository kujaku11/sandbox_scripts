#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 11:48:56 2020

@author: peacock
"""

from pathlib import Path
import shutil
from mtpy.usgs import zen_processing as zp

station_path = Path(r"/mnt/hgfs/MT_Data/GV2020/gv161/TS")
copy_path = Path(r"/mnt/hgfs/MT_Data/GV2020/EDI_Files_birrp")
# copy = True
copy = False
index = {4: -1, 256: -1, 4096: -1}

# copy = True
if not copy:
    plot = True
else:
    plot = False

edi_list = []
for df in [4096, 256, 4]:
    bf_path = Path.joinpath(station_path, "BF", str(df))
    edi_list.append(list(bf_path.glob("*.edi"))[index[df]])

zp_obj = zp.Z3D2EDI()
zp_obj.station_ts_dir = station_path.as_posix()
c_edi = zp_obj.combine_edi_files(
    edi_list, sr_dict={4096: (1000.0, 12.5), 256: (12.49, 0.12), 4: (0.119, 0.00001)}
)
if plot:
    rp = zp_obj.plot_responses(edi_list + [c_edi])

if copy:
    shutil.copy(c_edi, Path.joinpath(copy_path, station_path.parts[-2] + ".edi"))
