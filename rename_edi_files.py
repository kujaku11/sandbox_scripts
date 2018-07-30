# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 11:32:58 2018

@author: jpeacock
"""

import os
import mtpy.core.mt as mt
import mtpy.usgs.usgs_archive as archive

# =============================================================================
# Inputs
# =============================================================================
#edi_path = r"c:\Users\jpeacock\Documents\iMush\imush_edi_files_final"

edi_path = r"c:\Users\jpeacock\Documents\iMush\edi_files_renamed"
#if not os.path.exists(sv_path):
#    os.mkdir(sv_path)

#ab_list = [chr(i) for i in range(ord('A'),ord('Z')+1)]   
#char_dict = dict([(index, alpha) for index, alpha in enumerate(ab_list, 1)])

# =============================================================================
# Rename EDI files and rename station
# =============================================================================
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi')]

lines = ['station,lat,lon,nm_elev']
for edi_fn in edi_list:
    mt_obj = mt.MT(edi_fn)
    nm_elev = archive.get_nm_elev(mt_obj.lat, mt_obj.lon)
    lines.append('{0},{1:.5f},{2:.5f},{3:.2f}'.format(mt_obj.station,
                                                      mt_obj.lat, 
                                                      mt_obj.lon,
                                                      nm_elev))
    
with open(os.path.join(edi_path, 'imush_station_locations_nm.csv'), 'w') as fid:
    fid.write('\n'.join(lines))
    
#    print(mt_obj.station)
#    new_station = '{0}{1:03}'.format(char_dict[int(mt_obj.station[0:2])], 
#                                     int(mt_obj.station[2:]))
#    mt_obj.station = new_station
#    print(mt_obj.station)
#    mt_obj.write_mt_file(save_dir=sv_path)