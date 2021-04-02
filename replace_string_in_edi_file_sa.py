# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:41:04 2018

@author: jpeacock
"""

import os

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\Rotated_W30N"
edi_list = [
    os.path.join(edi_path, fn) for fn in os.listdir(edi_path) if fn.endswith(".edi")
]

for edi_fn in edi_list:
    with open(edi_fn, "r") as fid:
        edi_str = fid.read()

    new_edi_str = edi_str.replace("Rotated_W30N", "Geomagnetic North")
    with open(edi_fn, "w") as fid:
        fid.write(new_edi_str)
