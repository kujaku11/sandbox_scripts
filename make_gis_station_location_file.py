# -*- coding: utf-8 -*-
"""
Created on Tue Dec 09 14:57:07 2014

@author: jpeacock-pr
"""

import os
import mtpy.core.mt as mt

#edi_path = r"c:\Users\jpeacock-pr\Documents\MonoBasin\LV_Wannamaker"
#edi_path = r"c:\Users\jpeacock\Google Drive\Mono_Basin\EDI_Files"

def make_gis_station_location_file(edi_path, save_path=None,
                                   fn_basename=None):
    edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
                if edi.find('.edi') > 0]
                    

    
    if fn_basename is None:
        fn_basename = 'Station_locations.csv'
    if save_path is None:
        sv_fn = os.path.join(edi_path, fn_basename)
    else:
        sv_fn = os.path.join(save_path, fn_basename)
        
    #--> write csv file
    sfid = file(sv_fn, 'w')
    
    header_line = '{0:},{1:},{2:},{3:}\n'.format('lon', 'lat', 
                                                  'elevation', 'Object-ID')
    lines = []
    lines.append(header_line)
    for ii, edi in enumerate(edi_list):
        mt_obj = mt.MT(fn=edi)
        line = '{1:.3f},{2:.3f},{3:.3f},{0:}\n'.format(mt_obj.station,
                mt_obj.lon, mt_obj.lat, mt_obj.elev)
        lines.append(line)
    
    sfid.writelines(lines)
    sfid.close()
    

make_gis_station_location_file(r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\EDI_Files_INV",
                               save_path=r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS",
                               fn_basename=r"MSHS_2016_Station_Locations.csv")     