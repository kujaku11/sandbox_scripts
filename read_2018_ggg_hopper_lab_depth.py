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

utm_zone = 32610
utm_gdf = gdf.to_crs(utm_zone)

# pointsToVTK(
#     fn.parent.joinpath(f"2018_hopper_lab_depth_{utm_zone}_km_ned").as_posix(),
#     utm_gdf.geometry.x.to_numpy() / 1000,
#     utm_gdf.geometry.y.to_numpy() / 1000,
#     -1 * utm_gdf.depth.to_numpy(),
#     {"depth": utm_gdf.depth.to_numpy()},
# )

pointsToVTK(
    fn.parent.joinpath(f"2018_hopper_lab_depth_{utm_zone}_m_enzm").as_posix(),
    utm_gdf.geometry.x.to_numpy(),
    utm_gdf.geometry.y.to_numpy(),
    -1 * utm_gdf.depth.to_numpy() * 1000,
    {"depth": utm_gdf.depth.to_numpy()},
)
