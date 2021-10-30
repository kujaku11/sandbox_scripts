# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:43:00 2021

@author: jpeacock
"""

from mth5.mth5 import MTH5
from mt_metadata.timeseries import Survey, Station, Run, Electric
import numpy as np

m = MTH5()
m.open_mth5(r"c:\Users\jpeacock\benchmark.h5", "w")

s = m.add_station("mt001")
r = s.add_run("001")

ex_metadata = Electric()
ex_metadata.time_period.start = "2020-01-01T00:00:00"
ex_metadata.time_period.end = "2020-01-01T12:00:00"
ex_metadata.component = "ex"
ex_metadata.sample_rate = 256

ex = r.add_channel("ex", "electric", None, channel_metadata=ex_metadata)
ex.replace_dataset(np.random.rand(11059200))

