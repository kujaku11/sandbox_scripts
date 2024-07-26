# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 15:14:30 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import numpy as np
from mtpy import MT, MTData, MTCollection

# =============================================================================
# Parameters
# =============================================================================
edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES")
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\ingenious\modem_inv\inv_01"
)

bounds = {"lat": np.array([39.49, 40.87]), "lon": np.array([-118.36, -116.5])}

md = MTData()
for fn in edi_path.glob("*.edi"):
    m = MT()
    m.read(fn)
    if (m.latitude >= bounds["lat"].min()) and (
        m.latitude <= bounds["lat"].max()
    ):
        if (m.longitude >= bounds["lon"].min()) and (
            m.longitude <= bounds["lon"].max()
        ):
            md.add_station(m)

md.to_shp(save_path.joinpath("bm_bv_dv_mt_stations.shp"))

print("\a")

with MTCollection() as mc:
    mc.open_collection(save_path.joinpath("bm_bv_dv_collection.h5"))
    mc.from_mt_data(md)

print("\a")
