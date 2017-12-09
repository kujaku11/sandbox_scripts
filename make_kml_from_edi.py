# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 10:40:47 2014

@author: jpeacock-pr
"""

import simplekml as skml
import mtpy.core.mt as mt
import os

edi_path = r"d:\Peacock\MTData\EDI_Folders\LV_EDI_Files"

edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.find('.edi')>0  and 'LV' not in edi]
                    
edi_list = [edi_fn for edi_fn in edi_list if int(edi_fn[-7:-4]) < 400 and
            int(edi_fn[-7:-4]) > 167]

kml_obj = skml.Kml()


for edi in edi_list:
    mt_obj = mt.MT(edi)
    pnt = kml_obj.newpoint(name=mt_obj.station, 
                           coords=[(mt_obj.lon, mt_obj.lat, mt_obj.elev)])
    pnt.style.labelstyle.color = skml.Color.white
    pnt.style.labelstyle.scale = .8
    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/dir_60.png'
    pnt.style.iconstyle.scale = .8

kml_obj.save(os.path.join(edi_path, "lv_mt_stations.kml"))
    
            
            
