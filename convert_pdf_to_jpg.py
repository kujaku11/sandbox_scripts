# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 12:13:44 2018

@author: jpeacock
"""

import os
import subprocess

fn_dir = r"c:\Users\jpeacock\Documents\ClearLake\Figures"

fn_list = [os.path.join(fn_dir, fn) for fn in os.listdir(fn_dir) if fn.endswith(".pdf")]

for fn in fn_list:
    std_out = subprocess.check_output(
        ["magick", "convert", "-density", "300", fn, "-flatten", fn[:-4] + ".jpg"]
    )
