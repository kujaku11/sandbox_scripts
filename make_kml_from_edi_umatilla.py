# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 10:40:47 2014

@author: jpeacock-pr
"""

import simplekml as skml
import mtpy.core.mt as mt
import os

#edi_path = r"d:\Peacock\MTData\SanPabloBay\EDI_Files_dp"
#edi_path = r"c:\Users\jpeacock\Documents\iMush\iMush_edited_edi_files_JRP"
#edi_path = r"c:\Users\jpeacock\Documents\ShanesBugs\Tongario_Hill\original"
#edi_path = r"d:\Peacock\MTData\LV\EDI_Files_dp"
edi_path = r"d:\Peacock\MTData\Umatilla\EDI_Files_birrp"

s_list = ['um{0:03}.edi'.format(ss) for ss in [100, 102, 104, 105, 107, 112,
                                           113, 114, 117, 120, 123, 124,
                                           126, 127, 132, 133, 133,
                                           134, 135, 136, 142, 143, 144, 145,
                                           149, 150, 151, 152, 153, 157, 158,
                                           159, 161, 162, 163, 164, 165, 166]]
                                           
#edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
#            if edi.find('.edi')>0]
edi_list = [os.path.join(edi_path, edi) for edi in s_list]
                    

kml_obj = skml.Kml()

arc_lines = [','.join(['id','name','lat','lon'])]
for ii, edi in enumerate(edi_list, 1):
    mt_obj = mt.MT(edi)
    pnt = kml_obj.newpoint(name=mt_obj.station, 
                           coords=[(mt_obj.lon, mt_obj.lat, mt_obj.elev)])
    pnt.style.labelstyle.color = skml.Color.white
    pnt.style.labelstyle.scale = .8
    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/dir_60.png'
    pnt.style.iconstyle.scale = .8
    arc_lines.append(','.join(['{0:d}'.format(ii), 
                      'um{0}'.format(mt_obj.station), 
                      '{0:.6f}'.format(mt_obj.lat), 
                      '{0:.6f}'.format(mt_obj.lon)]))

kml_obj.save(os.path.join(edi_path, "umatilla_mt_stations.kml"))

with open(os.path.join(edi_path, 'umatilla_mt_station.csv'), 'w') as fid:
    fid.write('\n'.join(arc_lines))
    
            
            
