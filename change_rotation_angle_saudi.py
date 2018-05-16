# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 11:10:23 2017

@author: jpeacock
"""

import os

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\renamed"
sv_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\renamed_01"

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\LP_Rotated\Rotated_30_deg"
sv_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\LP_Rotated\GeomagneticNorth"
if not os.path.exists(sv_path):
    os.mkdir(sv_path)

edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
            if ss.endswith('.edi')]

for edi in edi_list:
    with open(edi, 'r') as fid:
        edi_str = fid.read()
    
    edi_str = edi_str.replace('3.000000e+01', '0.000000e+00')           
    
    with open(os.path.join(sv_path, os.path.basename(edi)), 'w') as fid:
        fid.write(edi_str)