# -*- coding: utf-8 -*-
"""

Created on Tue Aug  1 15:11:59 2023

:author: Jared Peacock

:license: MIT

"""

import shutil
from pathlib import Path


# data_folder = r"d:\WD SmartWare.swstor\IGSWMBWGLTGG032\Volume.b5634234.da89.11e2.aa2b.806e6f6e6963\MT\SCEC"
# data_folder = "/mnt/hgfs/MT_Data/GB2022"
# data_folder = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\GZ2021")
data_folder = Path(r"c:\MT\BV2023")
for station in data_folder.iterdir():
    if station.is_dir():
        for station_file in station.iterdir():
            if station_file.is_file() and station_file.suffix == ".h5":
                print(station_file)
                shutil.move(
                    station_file, data_folder.joinpath("mth5", station_file.name)
                )
