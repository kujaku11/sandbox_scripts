# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 15:18:59 2021

@author: jpeacock
"""

import numpy as np
import pandas as pd
from pathlib import Path


from mt_metadata.timeseries.filters.frequency_response_table_filter import (
    FrequencyResponseTableFilter,
)
from mt_metadata.timeseries.filters.channel_response_filter import ChannelResponseFilter

fap_filter = FrequencyResponseTableFilter(
    name="correction_factor_bx",
    units_in="nT",
    units_out="nT",
    comments="Frequency dependent correction for magnetic field",
)

bx_cal_file = Path(r"c:\Users\jpeacock\Documents\test_data\LEMI-424_N131_Bx.rsp")

df = pd.read_csv(
    bx_cal_file, delimiter="\s+", names=["frequency", "amplitude", "phase"]
)

df.phase = np.deg2rad(df.phase)

# frequencies = []
# amplitudes = []
# phases = []
# with open(bx_cal_file, 'r') as fin:
#     for line in fin:
#         frequency, amplitude, phase = line.strip().split()
#         frequencies.append(float(frequency))
#         amplitudes.append(float(amplitude))
#         phases.append(float(phase))
# fap_filter.frequencies = np.array(frequencies, dtype=float)
# fap_filter.amplitudes = np.array(amplitudes, dtype=float)
# fap_filter.phases = np.deg2rad(phases, dtype=float)

fap_filter.frequencies = df.frequency.to_numpy()
fap_filter.amplitudes = df.amplitude.to_numpy()
fap_filter.phases = df.phase.to_numpy()

bx_filter = ChannelResponseFilter(filters_list=[fap_filter])

bx_response = bx_filter.to_obspy()
