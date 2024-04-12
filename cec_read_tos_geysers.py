# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 13:33:57 2019

@author: jpeacock

read in top of steam to larger_grid model coordinates
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd
from pyevtk.hl import pointsToVTK
from mtpy.utils.gis_tools import project_point

# =============================================================================
fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\tos_points.txt")

model_east, model_north = project_point(-122.796391, 38.812566, 4326, 32610)

df = pd.read_csv(fn)

x = (df.X.to_numpy() - model_east) / 1000
y = (df.Y.to_numpy() - model_north) / 1000
z = df.Elevation.to_numpy() * 0.3048 / 1000

pointsToVTK(
    fn.parent.joinpath(f"{fn.stem}_cec_larger_grid").as_posix(),
    x,
    y,
    z,
    {"depth": z},
)

df_new = pd.DataFrame({"northing": y, "easting": x, "depth": z})
df_new.to_csv(
    fn.parent.joinpath("CEC", f"{fn.stem}_cec_larger_grid_02.csv"), index=False
)
