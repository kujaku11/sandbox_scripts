# -*- coding: utf-8 -*-
"""
Created on Sat May 27 15:50:21 2017

@author: jpeacock-pr
"""

import os
import numpy as np


fn_path = r"c:\MT\MusicValley\mv215\TS"

comp = "ey"

fn_list = [
    os.path.join(fn_path, fn) for fn in os.listdir(fn_path) if fn.endswith(comp.upper())
]

for fn in fn_list[0:-1]:
    print "-" * 40
    print "   Reading: {0}".format(fn)
    with open(fn, "r") as fid:
        header_list = []
        for ii in range(22):
            header_list.append(fid.readline())

    x = np.loadtxt(fn, skiprows=22)
    x *= -1
    ts = x.astype("S18")
    print "    Flipped Polarity <->"
    # write the file
    with open(fn, "w") as fid:
        fid.writelines(header_list)
        fid.write("\n".join(list(ts)))

    print "    Wrote: {0}".format(fn)
