#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 14:17:24 2022

@author: peacock
"""

from pathlib import Path
from mth5.mth5 import MTH5
import pandas as pd


archive_dir = Path("/mnt/hgfs/MT_Data/SCEC/Archive")
survey_df = pd.read_csv(r"/mnt/hgfs/MT_Data/SCEC/ssaf_survey_summary.csv")

for station_dir in archive_dir.iterdir():
    try:
        h5 = list(station_dir.glob("*.h5"))[0]
        m = MTH5()
        m.open_mth5(h5, "a")
        station = m.survey_group.stations_group.groups_list[0]
        station_group = m.get_station(station)
        survey_df.loc[survey_df.station==station, "end"] = station_group.metadata.time_period.end
        m.close_mth5()
    except IndexError:    
        print(f"Skipping {station_dir}")
        
    