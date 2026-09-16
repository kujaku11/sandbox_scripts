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
import pandas as pd
import numpy as np

from mt_metadata.timeseries import Magnetic, Electric

# =============================================================================

edi_path = Path(r"c:/Users/jpeacock/OneDrive - DOI/MTData/SAGE2026/mth5/EDI_Files_aurora/edited/geographic_north")
df = pd.read_csv(r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\survey_summary.csv")
channel_dict = {"hx": 1, "hy": 2, "hz": 3, "ex": 4, "ey": 5}

for fn in list(edi_path.glob("*.edi")):
    m = MT(fn)
    m.read()
    m.station_metadata.comments.value = ""
    row = df.loc[df["station"] == m.station]

    m.survey_metadata.id = "SAGE2026"
    m.survey_metadata.acquired_by.author = (
        "SAGE Students"
    )
    m.survey_metadata.country = "USA"
    m.survey_metadata.datum = "WGS84"
    m.survey_metadata.geographic_name = "Valles Caldera National Preserve, New Mexico"
    m.survey_metadata.name = "SAGE 2026"
    m.survey_metadata.project = "SAGE 2026"
    m.survey_metadata.project_lead.author = "Jared Peacock"
    m.survey_metadata.project_lead.email = "jpeacock@usgs.gov"
    m.survey_metadata.project_lead.organization = "U.S. Geological Survey"
    m.survey_metadata.release_license = "CC0-1.0"
    m.survey_metadata.summary = (
        "The project is funded by SAGE for educational purposes and to understand the magmatic system of the Valles Caldera "
        "using magnetotelluric data to image the subsurface in 3D."
    )

    m.station_metadata.acquired_by.author = "SAGE Students"
    m.station_metadata.geographic_name = "Valles Caldera National Preserve, New Mexico"
    m.station_metadata.acquired_by.comments = None
    m.station_metadata.acquired_by.organization = "SAGE"
    m.station_metadata.channel_layout = "L"
    m.station_metadata.comments.value = row.notes.values[0]
    m.station_metadata.data_type = "BBMT"
    m.station_metadata.location.declination.comments = "from https://ngdc.noaa.gov/geomag/calculators/magcalc.shtml#declination"
    m.station_metadata.location.declination.model = "WMM-2021"
    m.station_metadata.location.declination.value = 7.9
    m.station_metadata.orientation.method = "compass"
    m.station_metadata.orientation.reference_frame = "geographic"
    m.station_metadata.provenance.comments = "Time series converted from Zen format to MTH5"
    m.station_metadata.provenance.software.author = "Jared Peacock"
    m.station_metadata.provenance.software.name = "MTH5"
    m.station_metadata.provenance.software.version = "0.6.8"
    m.station_metadata.provenance.submitter.author = "Jared Peacock"
    m.station_metadata.provenance.submitter.email = "jpeacock@usgs.gov"
    m.station_metadata.provenance.submitter.organization = "U.S. Geological Survey"
    m.station_metadata.location.state = "New Mexico"

    m._rotation_angle = np.repeat(0.0, len(m.period))

    try:
        m.station_metadata.runs.remove("")
    except KeyError:
        pass

    for ch in ["ex", "ey"]:
        ch_obj = Electric(component=ch)
        ch_obj.channel_number = channel_dict[ch]
        ch_obj.dipole_length = row[f"dipole_{ch}"].values[0]
        ch_obj.channel_id = ch_obj.channel_number
        if ch == "ey":
            ch_obj.measurment_azimuth = 90
            ch_obj.translated_azimuth = 90
            ch_obj.positive.y2 = ch_obj.dipole_length
        else:
            ch_obj.positive.x2 = ch_obj.dipole_length
        m.station_metadata.runs[0].add_channel(ch_obj)
    for ii, ch in enumerate(["hx", "hy", "hz"], 1):
        ch_obj = Magnetic(component=ch)
        ch_obj.channel_number = channel_dict[ch]
        ch_obj.channel_id = ch_obj.channel_number
        ch_obj.sensor.id = str(row[f"{ch}"].values[0])
        if ch == "hy":
            ch_obj.measurment_azimuth = 90
            ch_obj.translated_azimuth = 90
        m.station_metadata.runs[0].add_channel(ch_obj)

    edi_obj = m.write(edi_path.joinpath(f"{m.station}_updated.edi"))
