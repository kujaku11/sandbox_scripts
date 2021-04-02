# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 14:39:00 2017

@author: jpeacock
"""

import os
import numpy as np

fn_path = r"/mnt/hgfs/MT_Data/GV2020/gv111/TS"

comp = "HY"

fn_list = [os.path.join(fn_path, fn) for fn in os.listdir(fn_path) if fn.endswith(comp)]

for fn in fn_list:
    print("-" * 40)
    print("    Reading: {0}".format(fn))
    with open(fn, "r") as fid:
        header = []
        for ii in range(23):
            header.append(fid.readline())

    x = np.loadtxt(fn, skiprows=1)
    x *= -1
    ts = x.astype("U18")

    print("    <-> Flipped Polarity")

    with open(fn, "w") as fid:
        fid.writelines(header)
        fid.write("\n".join(list(ts)))

    print("    Wrote: {0}".format(fn))
