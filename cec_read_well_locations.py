# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 16:14:50 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd

from mtpy.utils.gis_tools import project_point
from pyevtk.hl import pointsToVTK

# =============================================================================

fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\water.intectors.txt")

df = pd.read_csv(fn, sep="\s+")

gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude)
)
gdf.to_file(fn.parent.joinpath(f"{fn.stem}.shp"))

model_center = {"latitude": 38.812566, "longitude": -122.796391}

model_east, model_north = project_point(
    model_center["longitude"], model_center["latitude"], 4326, 32610
)

x, y = project_point(df.Longitude, df.Latitude, 4326, 32610)

x = (x - model_east) / 1000
y = (y - model_north) / 1000
z = df.Depth.to_numpy() * 0.304 / 1000


pointsToVTK(
    fn.parent.joinpath("gz_injection_wells").as_posix(),
    y,
    x,
    np.zeros(x.size),
    data={"depth": z},
)
