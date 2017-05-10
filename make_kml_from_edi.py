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
edi_path = r"c:\Users\jpeacock\Documents\iMush\imush_edi_files_final"
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.find('.edi')>0]
                    

kml_obj = skml.Kml()


for edi in edi_list:
    mt_obj = mt.MT(edi)
    pnt = kml_obj.newpoint(name=mt_obj.station, 
                           coords=[(mt_obj.lon, mt_obj.lat, mt_obj.elev)])
    pnt.style.labelstyle.color = skml.Color.white
    pnt.style.labelstyle.scale = .8
    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/dir_60.png'
    pnt.style.iconstyle.scale = .8

kml_obj.save(os.path.join(edi_path, "imush_final_all.kml"))
    
            
            
