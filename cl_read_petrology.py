# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 17:01:31 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from pyevtk.hl import pointsToVTK
import pandas as pd
import geopandas as gpd

# =============================================================================

fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\Primitive comps_lat_long_P_T.csv"
)

df = pd.read_csv(fn)
df.age.fillna(0)
df.composition.fillna("BHK")
df["depth_29"] = -1000 * 2.9 * 9.8 * df.pressure
df["depth_30"] = -1000 * 3.0 * 9.8 * df.pressure
df["depth_31"] = -1000 * 3.1 * 9.8 * df.pressure
df["water"] += 1

gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.longitude, df.latitude)
)
gdf.crs = "epsg:4326"
gdf = gdf.to_crs(epsg=32610)

pointsToVTK(
    fn.parent.joinpath(f"{fn.stem}_enzm").as_posix(),
    gdf.geometry.x.to_numpy(dtype=float),
    gdf.geometry.y.to_numpy(dtype=float),
    gdf.depth_30.to_numpy(dtype=float),
    data={
        "water": gdf.water.to_numpy(dtype=float),
        "age": gdf.age.to_numpy(dtype=float),
        "composition": gdf.composition.to_numpy(dtype=int),
        "temperature": gdf.temperature.to_numpy(dtype=float),
        "depth_29": gdf.depth_29.to_numpy(dtype=float),
        "depth_30": gdf.depth_30.to_numpy(dtype=float),
        "depth_31": gdf.depth_31.to_numpy(dtype=float),
    },
)
