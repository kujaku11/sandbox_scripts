# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 15:57:59 2017

@author: jpeacock
"""

from pathlib import Path
from mth5.io.zen import Z3D

station_folder = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2024")

for fn in station_folder.rglob("*.z3d"):
    z3d_obj = Z3D(fn)
    z3d_obj.read_all_info()

    channel = z3d_obj.metadata.ch_cmp.upper()
    st = z3d_obj.schedule.Time.replace(":", "")
    sd = z3d_obj.schedule.Date.replace("-", "")
    sr = int(z3d_obj.sample_rate)
    sv_fn = station_folder.joinpath(
        f"{z3d_obj.station}_{sd}_{st}_{sr}_{channel}.Z3D"
    )

    fn.replace(sv_fn)

    print("renamed {0} to {1}".format(fn, sv_fn))
