# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:44:47 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd
import geopandas as gpd

# =============================================================================

tumby_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MonoBasin\Mono_Lake_2015\spencer_gulf\Tumby.csv"
)
hybrid_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MonoBasin\Mono_Lake_2015\spencer_gulf\Marine_Hybrid.csv"
)

columns = [
    "station",
    "latitude",
    "longitude",
    "easting",
    "northing",
    "elevation",
]
df_tumby = pd.read_csv(tumby_fn, sep="\s+", names=columns)
df_hybrid = pd.read_csv(hybrid_fn, sep="\s+", names=columns)

df = pd.concat([df_tumby, df_hybrid])

gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=4326
)
gdf.to_file(
    r"c:\Users\jpeacock\OneDrive - DOI\MonoBasin\Mono_Lake_2015\spencer_gulf\spencer_gulf_mt_stations.shp"
)
