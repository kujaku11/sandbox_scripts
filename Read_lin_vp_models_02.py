# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 10:45:41 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import interpolate
import geopandas as gpd
from pyevtk.hl import gridToVTK


# =============================================================================
fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\2022_qi_seismic_model_ClearLake\ModelinGEOS"
)
df = pd.read_csv(
    fn,
    delim_whitespace=True,
    header=None,
    usecols=[0, 1, 2, 3, 5],
    names=["lon", "lat", "z", "vp", "moho"],
)
