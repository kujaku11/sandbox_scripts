# -*- coding: utf-8 -*-
"""

Created on Sun Sep 12 20:38:16 2021

:author: Jared Peacock

:license: MIT

"""
from pathlib import Path
import numpy as np
from mtpy.core import ts


fn = Path(r"c:\MT\GZ2021\RR\e_mag_volts_rs50\0854\20210405.npy")
date = f"{fn.stem[0:4]}-{fn.stem[4:6]}-{fn.stem[6:8]}"

h = np.fromfile(fn)
h = np.nan_to_num(h)
h[h>10] = 0

t = ts.MTTS()
t.ts = h
t.sampling_rate = 50.
t.start_time_utc = f"{date}T00:00:00"

