#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:55:36 2020

@author: peacock
"""

import numpy as np
import pandas as pd
from pathlib import Path

ant_cal_fn = r"/mnt/hgfs/peaco/Documents/MT/amtant.cal"
sv_path = Path(r"/mnt/hgfs/peaco/Documents/MT/birrp_calibrations")
if not sv_path.exists():
    sv_path.mkdir()

fn_path = Path(ant_cal_fn)

### open file
with open(ant_cal_fn, "r") as fid:
    lines = fid.readlines()

### sort data
data = {}
for line in lines:
    line = line.strip()
    if line.find("antenna") > 0:
        freq = float(line.split()[-1]) * 2 * np.pi
    elif len(line) > 0:
        ant, amp, phase, amp2, phase2 = [float(ii) for ii in line.split()]
        if ant != 0:
            z_real = amp * np.cos(phase / 1000.0)
            z_imag = amp * np.sin(phase / 1000.0)

            z_real2 = amp * np.cos(phase / 1000.0)  #
            z_imag2 = amp * np.sin(phase / 1000.0)  #
            entry = [freq, amp, phase, amp2, phase2, z_real, z_imag, z_real2, z_imag2]

            if ant not in list(data.keys()):
                data[int(ant)] = [[1] * 9]  # birrp wants first line to be a scale
            data[ant].append(entry)

for key in list(data.keys()):
    sv_fn = Path.joinpath(sv_path.parent, sv_path.name, "{0}.csv".format(key))
    df = pd.DataFrame(
        data[key],
        columns=[
            "freq",
            "amp",
            "phase",
            "amp2",
            "phase2",
            "z_real",
            "z_imag",
            "z_real2",
            "z_imag2",
        ],
    )
    df.to_csv(sv_fn, columns=["freq", "z_real", "z_imag"], index=False, header=False)
