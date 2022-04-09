# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 10:43:48 2021

@author: jpeacock
"""
from pathlib import Path
import pickle
from mt_metadata.timeseries.filters import PoleZeroFilter, ChannelResponseFilter

pz_filter = PoleZeroFilter(
    name="correction_factor_bx",
    units_in="nT",
    units_out="nT",
    comments="Frequency dependent correction for magnetic field channel Hx",
    normalization_factor=1,
)
bx_cal_file = Path(r"c:\Users\jpeacock\OneDrive - DOI\mt\LEMI-424_N131_Bx.zpk")
with open(bx_cal_file, "rb") as fin:
    zpk = pickle.load(fin)
    pz_filter.poles = zpk.poles
    pz_filter.zeros = zpk.zeros
    bx_filter = ChannelResponseFilter(filters_list=[pz_filter])
    bx_response = bx_filter.to_obspy()
