# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 11:10:23 2017

@author: jpeacock
"""

import os

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\Edited"
sv_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\Edited_01"
if not os.path.exists(sv_path):
    os.mkdir(sv_path)

edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
            if ss.endswith('.edi')]

for edi in edi_list:
    with open(edi, 'r') as fid:
        edi_str = fid.read()
    
    edi_str = edi_str.replace('0.000000e+00', '-3.40000e+01')           
    
    with open(os.path.join(sv_path, os.path.basename(edi)), 'w') as fid:
        fid.write(edi_str)