# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 12:37:19 2015

@author: jpeacock
"""

import mtpy.usgs.zonge as zonge
import os

dir_path = r"c:\Users\jpeacock\Documents\iMush\iMush_2016_avg_files"

avg_list = [os.path.join(dir_path, avg) for avg in os.listdir(dir_path)
            if avg[-4:]=='.avg']
                
for avg_fn in avg_list:
    station = os.path.basename(avg_fn[:-6])
    za = zonge.ZongeMTAvg()
    za.write_edi_from_avg(avg_fn, station,
                          mtedit_cfg_file=None,
                          copy_path=os.path.join(dir_path, 'iMush_EDI_Files_2016'))
    