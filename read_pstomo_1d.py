# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 15:15:50 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd

import numpy as np

# =============================================================================
fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\seismic\2024_furlong_starting_1d_vel_p.txt"
)

df = pd.read_csv(fn, delimiter="\s+", names=["depth", "vp"])

d = np.linspace(df.depth.min(), df.depth.max(), 150)
v = np.zeros_like(d)
for ii, dd in enumerate(d):
    v[ii] = df.loc[(df.depth <= dd)].vp.array[-1]
