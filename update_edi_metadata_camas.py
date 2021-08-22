# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:16:13 2018

@author: jpeacock
"""

import os
import mtpy.core.mt as mt

edi_path = r"d:\Peacock\MTData\SAGE_2018\EDI_Files_birrp"

survey_cfg = r"d:\Peacock\MTData\SAGE_2018\sage_birrp.cfg"


sv_path = os.path.join(edi_path, "final")
if not os.path.exists(sv_path):
    os.mkdir(sv_path)
for fn in os.listdir(edi_path):
    if not fn.endswith(".edi"):
        continue
    mt_obj = mt.MT(fn=os.path.join(edi_path, fn))
    mt_obj.station = "s18{0}".format(mt_obj.station)
    mt_obj.read_cfg_file(survey_cfg)
    mt_obj.write_mt_file(save_dir=sv_path)
