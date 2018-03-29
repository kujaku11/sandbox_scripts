# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:16:13 2018

@author: jpeacock
"""

import os
import mtpy.core.mt as mt

edi_path = r"d:\Peacock\MTData\MountainHome\EDI_Files_birrp_edit"

survey_cfg = r"D:\Peacock\MTData\MountainHome\camas_mt_2018.cfg"


sv_path = os.path.join(edi_path, 'final')
if not os.path.exists(sv_path):
    os.mkdir(sv_path)
for fn in os.listdir(edi_path):
    if not fn.endswith('.edi'):
        continue
    mt_obj = mt.MT(fn=os.path.join(edi_path, fn))
    mt_obj.read_cfg_file(survey_cfg)
    mt_obj.write_mt_file(save_dir=sv_path)
            
            