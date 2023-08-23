# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 10:34:48 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mtpy import MT

from mt_metadata.timeseries import Magnetic, Electric

# =============================================================================

edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\SAGE\EDI_Files\2023")

for fn in list(edi_path.glob("*.edi")):
    m = MT(fn)
    m.read()

    try:
        sn = int(m.station)
        m.station = f"val{sn:003}"
    except ValueError:
        pass
    m.station_metadata.comments = ""

    try:
        m.station_metadata.runs.remove("")
    except KeyError:
        pass

    for ch in ["ex", "ey"]:
        ch_obj = Electric(component=ch)
        ch_obj.channel_number = 4
        ch_obj.dipole_length = 50
        ch_obj.channel_id = ch_obj.channel_number
        if ch == "ey":
            ch_obj.measurment_azimuth = 90
            ch_obj.translated_azimuth = 90
            ch_obj.channel_number = 5
            ch_obj.positive.y2 = 50
        else:
            ch_obj.positive.x2 = 50
        m.station_metadata.runs[0].add_channel(ch_obj)
    for ii, ch in enumerate(["hx", "hy", "hz"], 1):
        ch_obj = Magnetic(component=ch)
        ch_obj.channel_number = ii
        ch_obj.channel_id = ch_obj.channel_number
        if ch == "hy":
            ch_obj.measurment_azimuth = 90
            ch_obj.translated_azimuth = 90
        m.station_metadata.runs[0].add_channel(ch_obj)

    m.rotate(-8)

    edi_obj = m.write()
