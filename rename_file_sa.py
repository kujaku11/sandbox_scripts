# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 14:36:06 2018

@author: jpeacock
"""

import os

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\GeomagneticNorth_original"
sv_path = os.path.join(edi_path, 'renamed')
if not os.path.exists(sv_path):
    os.mkdir(sv_path)
    
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi')]

for edi_fn in edi_list:
    station = os.path.basename(edi_fn)[0:-4]
    if 'med' not in station:
        station = '{0}{1}'.format('med', station)
    with open(edi_fn, 'r') as fid:
        edi_str = fid.read()
        
    begin = edi_str.find('DATAID=')
    begin = edi_str[begin:].find('=')+begin+1
    end = edi_str[begin:].find('\n')+begin
    replace_str = edi_str[begin:end]
    new_edi_str = edi_str.replace(replace_str, station)
    
    with open(os.path.join(sv_path, station+'.edi'), 'w') as fid:
        fid.write(new_edi_str)