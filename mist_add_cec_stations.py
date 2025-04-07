# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 14:36:11 2025

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mtpy import MTData, MT
from mtpy.modeling import StructuredGrid3D

# =============================================================================

edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\MIST\cec_edi_files\edited")

md = MTData()
md.from_modem(
    r"c:\Users\jpeacock\OneDrive - DOI\MIST\modem_inv\inv_02\mist_modem_data_z03_t02_tec.dat"
)

s = StructuredGrid3D()
s.from_modem(
    r"c:\Users\jpeacock\OneDrive - DOI\MIST\modem_inv\inv_02\mist_sm30_topo.rho"
)
s.center_point = md.center_point

station_list = [
    "L1x08S",
    "L1x24S",
    "L1x28S",
    "L1x60S",
    "L1x80S",
    "L1x92S",
    "L2x16S",
    "L2x68S",
    "L2x92S",
    "L3x08S",
    "L3x40S",
    "L3x56S",
    "L3x64S",
    "L4x00W",
    "L4x30W",
    "L4x95W",
    "L4x115E",
    "L4x138E",
    "L4x154E",
    "SSx01",
    "SSx04",
    "SSx08",
    "SSx11",
    "SSx28",
    "SSx40",
    "SSx36",
    "SSx34",
    "SSx20",
    "SSx13",
    "SSx45",
    "SSx43",
    "SSx41",
]

periods = md.get_periods()
for station in station_list:
    mt_obj = MT()
    mt_obj.read(edi_path.joinpath(f"{station}.edi"))
    mt_obj.compute_model_z_errors(error_value=5, error_type="eigen")
    try:
        md.add_station(
            mt_obj,
            compute_relative_location=False,
            survey="data",
            interpolate_periods=periods,
        )
    except Exception as error:
        print(error)
        print(station)


md.compute_relative_locations()
md.center_stations(s)
md.project_stations_on_topography(s)
md.to_modem(
    r"c:\Users\jpeacock\OneDrive - DOI\MIST\modem_inv\inv_02\mist_modem_data_z03_t02_tec_cec.dat"
)
