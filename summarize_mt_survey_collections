#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 21:10:54 2020

@author: peacock
"""

import pandas as pd
from pathlib import Path
from mtpy.usgs import z3d_collection as zc

tol_dict = {4096: {'s_diff': 5 * 60,
                   'min_points': 2**18},
            256: {'s_diff': 3 * 3600,
                  'min_points': 2**19},
            4: {'s_diff': 4 * 3600,
                'min_points': 2**14}}

survey_path = Path('/mnt/hgfs/MT_Data/GV2020')
calibration_path = r"/mnt/hgfs/MT_Data/birrp_calibrations"
sdfn = survey_path.joinpath('gv_summary_df.csv')

if sdfn.exists():
    sdf = pd.read_csv(sdfn)
    sdf = sdf.infer_objects()

else:
    c_obj = zc.Z3DCollection()
    sdf = c_obj.summarize_survey(survey_path, 
                                 calibration_path=calibration_path)

sdf['start'] = pd.to_datetime(sdf.start)

info_list = []
for station in sdf.station.unique():
    station_df = sdf[sdf.station == station]
    for sr in station_df.sampling_rate.unique():
        sr_df = station_df[station_df.sampling_rate == sr]
        for start in sr_df.start.unique():
            block = int(sr_df[sr_df.start == start].block.median())
            s_dict = {'station':station,
                      'sampling_rate': sr,
                      'block': block,
                      'start': start}

            s1 = start - pd.Timedelta(tol_dict[sr]['s_diff'])
            s2 = start + pd.Timedelta(tol_dict[sr]['s_diff'])
            rr_df = sdf[(sdf.start >= s1) & (sdf.start <= s2) &
                        (sdf.station != station)]
            s_dict['rr_station'] = rr_df.station.unique().tolist()
            info_list.append(s_dict)

info_df = pd.DataFrame(info_list)
info_df.rr_station = info_df.rr_station.astype(str)

processing_list = []
for station in info_df.station.unique():
    station_df = info_df[info_df.station == station]
    rr_list = station_df.rr_station.mode()[0]
    station_entry = {'station':station,
                     'rr_station': rr_list,
                     'block_4096': None,
                     'block_256': None,
                     'block_4': [0]}

    for sr in station_df.sampling_rate.unique():
        sr_df = station_df[(station_df.sampling_rate == sr) &
                           (station_df.rr_station == rr_list)]

        station_entry['block_{0:.0f}'.format(sr)] = sr_df.block.unique().tolist()

    processing_list.append(station_entry)
