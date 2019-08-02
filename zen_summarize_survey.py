# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 16:32:19 2019

@author: jpeacock
"""
import os
import glob
import json
from mtpy.usgs import zen

survey_dir = r"d:\Peacock\MTData\SCEC" 

survey_dict = {}

for station in os.listdir(survey_dir):
    station_dir = os.path.join(survey_dir, station)
    if os.path.isdir(station_dir):
        z3d_list = glob.glob(os.path.join(station_dir, '*.Z3D'))
        if len(z3d_list) == 0:
            continue
        for z3d_fn in z3d_list:
            z3d_obj = zen.Zen3D(fn=z3d_fn)
            z3d_obj.read_all_info()
            dt_key = z3d_obj.zen_schedule.isoformat()
            if not dt_key in survey_dict.keys():
                survey_dict[dt_key] = {}
            if not z3d_obj.station in survey_dict[dt_key].keys():
                survey_dict[dt_key][z3d_obj.station] = {'comp':[],
                                                        'df':[],
                                                        'azm':[]}
            survey_dict[dt_key][z3d_obj.station]['comp'].append(z3d_obj.component)
            survey_dict[dt_key][z3d_obj.station]['df'].append(z3d_obj.df)
            survey_dict[dt_key][z3d_obj.station]['azm'].append(z3d_obj.azimuth)
            
with open(os.path.join(survey_dir, 'survey_summary.txt'), 'w') as fid:
    json.dump(survey_dict, fid)
    
lines = []
for d_key in sorted(list(survey_dict.keys())):
    lines.append('=== {0} ==='.format(d_key))
    for s_key in sorted(list(survey_dict[d_key].keys())):
        lines.append('{0}{1}'.format(' '*4, s_key))

with open(os.path.join(survey_dir, 'survey_summary.dat'), 'w') as fid:
    fid.write('\n'.join(lines))
    