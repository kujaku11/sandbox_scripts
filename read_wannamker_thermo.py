# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 13:04:34 2025

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import numpy as np
import pandas as pd

from mtpy import MTData, MT
from mtpy.core import MTDataFrame

# =============================================================================

utm_epsg = 32612
block_len = 5
fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\utah\thermo_survey\ThermoXs"
)

with fn.open() as fid:
    lines = fid.readlines()

sites = [ii for ii, line in enumerate(lines) if line.startswith("site")]


def read_block(block):
    keys = [
        "res_xx",
        "res_xx_error",
        "res_xy",
        "res_xy_error",
        "frequency",
        "res_yx",
        "res_yx_error",
        "res_yy",
        "res_yy_error",
        "phase_xx",
        "phase_xx_error",
        "phase_xy",
        "phase_xy_error",
        "phase_yx",
        "phase_yx_error",
        "phase_yy",
        "phase_yy_error",
        "t_zx_real",
        "t_zx_imag",
        "t_zx_error",
        "t_zy_real",
        "t_zy_imag",
        "t_zy_error",
    ]
    values = [
        float(ff) for ff in " ".join([line.strip() for line in block]).split()
    ]

    return dict([(key, value) for key, value in zip(keys, values)])


md = MTData()
for site_index in sites:
    site_name = lines[site_index].strip().replace("site", "thermo")
    site_location = lines[site_index + 1].strip().split()
    site_easting = float(site_location[2])
    site_northing = float(site_location[3])
    n_periods = int(lines[site_index + 2].strip().split()[0])

    data = []
    for block_index in range(
        site_index + 3, site_index + 3 + n_periods * block_len, block_len
    ):
        data.append(read_block(lines[block_index : block_index + block_len]))

    df = pd.DataFrame(data)
    df["t_zx"] = df.apply(
        lambda row: row["t_zx_real"] + 1j * row["t_zx_imag"], axis=1
    )
    df["t_zy"] = df.apply(
        lambda row: row["t_zy_real"] + 1j * row["t_zy_imag"], axis=1
    )
    df["period"] = 1.0 / df.frequency

    df["res_xx_error"] = df.res_xx_error * df.res_xx * 2.303
    df["res_xy_error"] = df.res_xy_error * df.res_xy * 2.303
    df["res_yx_error"] = df.res_yx_error * df.res_yx * 2.303
    df["res_yy_error"] = df.res_yy_error * df.res_yy * 2.303
    mt_df = MTDataFrame(data=df)
    mt_df.station = site_name
    mt_df.survey = "thermo"
    mt_df.east = site_easting
    mt_df.north = site_northing
    mt_df.utm_epsg = utm_epsg

    mt_obj = MT()
    mt_obj.from_dataframe(mt_df)
    mt_obj.write(fn.parent.joinpath(f"{site_name}.edi"))
    p = mt_obj.plot_mt_response(plot_num=2)
    p.save_plot(fn.parent.joinpath(f"{site_name}.png"), fig_dpi=300)
    md.add_station(mt_obj, compute_relative_location=False)
