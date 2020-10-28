# -*- coding: utf-8 -*-
"""
Created on Thu Aug 04 18:02:56 2016

@author: jpeacock-pr
"""

import os
import shutil

data_folder = r"d:\WD SmartWare.swstor\IGSWMBWGLTGG032\Volume.b5634234.da89.11e2.aa2b.806e6f6e6963\MT\SCEC"
# data_folder = '/mnt/hgfs/MT/SCEC'
for folder in os.listdir(data_folder):
    station_path = os.path.join(data_folder, folder)
    if os.path.isdir(station_path) is True:
        ts_path = os.path.join(station_path, "TS")
        if os.path.isdir(ts_path) is True:
            shutil.rmtree(ts_path)
            print("Removed {0}".format(ts_path))
