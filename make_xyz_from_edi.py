# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 10:40:47 2014

@author: jpeacock-pr
"""

import mtpy.core.mt as mt
import os

edi_path = r"d:\Peacock\MTData\Camas\EDI_Files_birrp\Edited\Rotated_13_deg\Camas_EDI_Files_new"

edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.find('.edi')>0]

lines = ['station,lat,lon,elev']
for edi in edi_list:
    mt_obj = mt.MT(edi)
    lines.append('{0},{1:.6f},{2:.6f},{3:.3f}'.format(mt_obj.station,
                                                      mt_obj.lat,
                                                      mt_obj.lon,
                                                      mt_obj.elev))

with open(os.path.join(edi_path, "camas_mt_stations_2018.txt"), 'w') as fid:
    fid.write('\n'.join(lines))
    
            
            
