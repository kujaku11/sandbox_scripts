# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 11:10:43 2019

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd
import numpy as np
from mtpy.utils.gis_tools import project_point
from pyevtk.hl import pointsToVTK

# =============================================================================

fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\Top_Felsite_Points_WGS84.csv"
)
model_east, model_north = project_point(-122.796391, 38.812566, 4326, 32610)

df = pd.read_csv(
    fn,
    delimiter=",",
    usecols=[0, 1, 2],
    names=["lat", "lon", "depth"],
    skiprows=1,
)

east, north = project_point(df.lon, df.lat, 4326, 32610)

x = (east - model_east) / 1000.0
y = (north - model_north) / 1000.0
z = (df.depth.to_numpy() / 3.25) / 1000.0

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
