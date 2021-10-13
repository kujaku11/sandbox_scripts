# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 15:43:30 2021

@author: jpeacock
"""

from mtpy.core import ts
import numpy as np

f = r"d:\2021UTC\n_mag_volts_rs50\0865\20210406.npy"

hx = np.fromfile(f)[200:]

t = ts.MTTS()
t.ts = hx
t.sampling_rate = 50
t.start_time_utc = "2020-01-01T00:00:00"

