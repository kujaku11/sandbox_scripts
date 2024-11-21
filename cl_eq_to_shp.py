# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 12:41:04 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd
import geopandas as gpd
# =============================================================================

base_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake")
fn_list = list(base_path.glob(r"cl_usgs_eq*.csv"))

df_list = []
for fn in fn_list[1:]:
    df_list.append(pd.read_csv(fn))
    
df = pd.concat(df_list)

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
gdf.crs = 4326

gdf.to_file(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\cl_usgs_eq.shp")