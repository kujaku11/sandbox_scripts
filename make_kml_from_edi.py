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
edi_path = r"c:\Users\jpeacock\Google Drive\Mono_Basin\INV_EDI_FILES"
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.find('.edi')>0]

kml_obj = skml.Kml()


for edi in edi_list:
    mt_obj = mt.MT(edi)
    kml_obj.newpoint(name=mt_obj.station, 
                     coords=[(mt_obj.lon, mt_obj.lat, mt_obj.elev)])

kml_obj.save(os.path.join(edi_path, "lv_2016_all_mt_sites.kml"))
    
            
            
