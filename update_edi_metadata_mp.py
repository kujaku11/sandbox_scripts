# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:16:13 2018

@author: jpeacock
"""

import os
import mtpy.core.mt as mt

edi_path = r"d:\Peacock\MTData\MountainPass\EDI_Files_ga"

survey_cfg = r"D:\Peacock\MTData\MountainPass\mp_zonge.cfg"


sv_path = os.path.join(edi_path, 'final')
if not os.path.exists(sv_path):
    os.mkdir(sv_path)
for fn in os.listdir(edi_path):
    if not fn.endswith('.edi'):
        continue
    mt_obj = mt.MT(fn=os.path.join(edi_path, fn))
    mt_obj.Notes.info_list = mt_obj.Notes.info_list[25:]
    mt_obj.Notes.info_dict = {}
    for info_str in mt_obj.Notes.info_list:
        key, value = info_str.split(':', 1)
        if key in ['notes', 'save_path', 'sampling_interval', 'station', 
                   'ts.number', 'ts.t0error', 'ts.t0offset', 'setup.number', 
                   'mtft.tsplot.pntrange', 'station_type', 'ts.frqband']:
            continue
        if 'phaseslope' in key:
            key  = 'mtft.'+key
        mt_obj.Notes.info_dict[key.strip()] = value.strip()
    mt_obj.read_cfg_file(survey_cfg)
    mt_obj.Copyright.Citation.author = ','.join(mt_obj.Copyright.Citation.author)
    mt_obj.Copyright.Citation.title = ','.join(mt_obj.Copyright.Citation.title)
    mt_obj.write_mt_file(save_dir=sv_path)
            
            