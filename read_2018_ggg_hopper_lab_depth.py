# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 16:32:14 2025

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd
import geopandas as gpd

from pyevtk.hl import pointsToVTK

# =============================================================================

fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\seismic\2018_ggg_hopper_lab_depths.csv"
)

df = pd.read_csv(fn, usecols=["latitude", "longitude", "depth"])
gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=4326
)

utm_gdf = gdf.to_crs(32611)

pointsToVTK(
    fn.parent.joinpath("2018_hopper_lab_depth_32611_km_ned").as_posix(),
    utm_gdf.geometry.x.to_numpy() / 1000,
    utm_gdf.geometry.y.to_numpy() / 1000,
    -1 * utm_gdf.depth.to_numpy(),
    {"depth": utm_gdf.depth.to_numpy()},
)
