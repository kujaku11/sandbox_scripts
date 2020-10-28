# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 16:30:37 2016

@author: jpeacock
"""

import os
import subprocess

dir_path = r"/mnt/hgfs/jpeacock/Google Drive/Antarctica/figures"

fn_list = [
    os.path.join(dir_path, fn)
    for fn in os.listdir(dir_path)
    if fn.find("Supp_Depth") == 0
]

for fn in fn_list:
    std_out = subprocess.call(
        ["convert", "-density", "300", fn, "{0}.pdf".format(fn[:-4])]
    )
