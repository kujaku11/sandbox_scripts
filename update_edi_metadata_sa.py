# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:16:13 2018

@author: jpeacock
"""

import os
import mtpy.core.mt as mt

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files"

folders = ["GeomagneticNorth"]

comb_cfg = r"C:\Users\jpeacock\Documents\SaudiArabia\sa_edi_combined.cfg"
bb_cfg = r"C:\Users\jpeacock\Documents\SaudiArabia\sa_edi_bb.cfg"

for folder in folders:
    edi_dir = os.path.join(edi_path, folder)
    sv_path = os.path.join(edi_path, folder + "_01")
    if not os.path.exists(sv_path):
        os.mkdir(sv_path)
    for fn in os.listdir(edi_dir):
        if not fn.endswith(".edi"):
            continue
        mt_obj = mt.MT(fn=os.path.join(edi_dir, fn))
        if fn.endswith("_c.edi"):
            mt_obj.read_cfg_file(comb_cfg)
        elif fn.endswith(".edi"):
            mt_obj.read_cfg_file(bb_cfg)
        mt_obj.Site.Location.coordinate_system = folder
        mt_obj.write_mt_file(save_dir=sv_path)
