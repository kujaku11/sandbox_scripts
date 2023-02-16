# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 10:24:22 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import unittest

import numpy as np
from mth5.timeseries import ChannelTS, RunTS
from mt_metadata.timeseries import Electric, Magnetic, Auxiliary, Run, Station

# =============================================================================

channel_list = []
common_start = "2020-01-01T00:00:00+00:00"
sample_rate = 1.0
n_samples = 4096
t = np.arange(n_samples)
data = np.sum(
    [
        np.cos(2 * np.pi * w * t + phi)
        for w, phi in zip(np.logspace(-3, 3, 20), np.random.rand(20))
    ],
    axis=0,
)

station_metadata = Station(id="mt001")
run_metadata = Run(id="001")

for component in ["hx", "hy", "hz"]:
    h_metadata = Magnetic(component=component)
    h_metadata.time_period.start = common_start
    h_metadata.sample_rate = sample_rate
    h_channel = ChannelTS(
        channel_type="magnetic",
        data=data,
        channel_metadata=h_metadata,
        run_metadata=run_metadata,
        station_metadata=station_metadata,
    )
    channel_list.append(h_channel)

for component in ["ex", "ey"]:
    e_metadata = Electric(component=component)
    e_metadata.time_period.start = common_start
    e_metadata.sample_rate = sample_rate
    e_channel = ChannelTS(
        channel_type="electric",
        data=data,
        channel_metadata=e_metadata,
        run_metadata=run_metadata,
        station_metadata=station_metadata,
    )
    channel_list.append(e_channel)

aux_metadata = Auxiliary(component="temperature")
aux_metadata.time_period.start = common_start
aux_metadata.sample_rate = sample_rate
aux_channel = ChannelTS(
    channel_type="auxiliary",
    data=np.random.rand(n_samples) * 30,
    channel_metadata=aux_metadata,
    run_metadata=run_metadata,
    station_metadata=station_metadata,
)
channel_list.append(aux_channel)

run_ts = RunTS(channel_list)
