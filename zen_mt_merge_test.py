# -*- coding: utf-8 -*-
"""
Created on Fri May 29 15:20:12 2015

@author: jpeacock-pr
"""

import mtpy.usgs.zen as zen
import numpy as np
import struct
import os


station_dir = r"d:\Peacock\MTData\Test\mb666"
fn_list = [
    os.path.join(station_dir, fn)
    for fn in os.listdir(station_dir)
    if fn.find("165016") > 0
]

zt_list = []
for fn in fn_list:
    zt = zen.Zen3D(fn)
    zt.read_z3d()
    zt_list.append(zt)
