# -*- coding: utf-8 -*-
"""
Created on Thu Aug 04 18:02:56 2016

@author: jpeacock-pr
"""

import shutil
from pathlib import Path

# data_folder = Path(r"d:\WD SmartWare.swstor\IGSWMBWGLTGG032\Volume.b5634234.da89.11e2.aa2b.806e6f6e6963\MT\SCEC")
# data_folder = Path("/mnt/hgfs/MT_Data/GZ2023")
data_folder = Path(r"c:\MT\GZ2023")
for station_path in data_folder.iterdir():

    if station_path.is_dir():
        for ts_path in station_path.iterdir():
            if ts_path.is_dir():
                if ts_path.name in ["TS"]:
                    shutil.rmtree(ts_path)
                    print(f"Removed {ts_path}")
                try:
                    fp = int(ts_path.name)
                    shutil.rmtree(ts_path)
                    print(f"Removed {ts_path}")
                except ValueError:
                    continue
            if ts_path.suffix in [".h5"]:
                print(f"Deleting {ts_path}")
                ts_path.unlink()
