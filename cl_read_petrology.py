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

fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\clearlake_petrology_newer.csv")

df = pd.read_csv(fn, skiprows=1, header=0)
df.age.fillna(0)
df["water"] += 1

df.series[df.series == "HMB"] = 1
df.series[df.series == "HMBA"] = 2
df.series[df.series == "HMA"] = 3
df.series[df.series == "HCB"] = 4

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
gdf.crs = "epsg:4326"
gdf = gdf.to_crs(epsg=32610)

for series in [1, 2, 3, 4]:
    vtk_df = gdf[gdf.series == series]

    pointsToVTK(
        fn.parent.joinpath(f"{fn.stem}_enzm_series_{series}").as_posix(),
        vtk_df.geometry.x.to_numpy(dtype=float),
        vtk_df.geometry.y.to_numpy(dtype=float),
        vtk_df.new_depth.to_numpy(dtype=float) * (-1000),
        data={
            "water": vtk_df.water.to_numpy(dtype=float),
            "series": vtk_df.series.to_numpy(dtype=int),
            f"temperature_{series}": vtk_df.temperature.to_numpy(dtype=float),
            "depth": vtk_df.new_depth.to_numpy(dtype=float),
        },
    )

pointsToVTK(
    fn.parent.joinpath(f"{fn.stem}_enzm").as_posix(),
    gdf.geometry.x.to_numpy(dtype=float),
    gdf.geometry.y.to_numpy(dtype=float),
    gdf.new_depth.to_numpy(dtype=float) * -1000,
    data={
        "water": gdf.water.to_numpy(dtype=float),
        "series": gdf.series.to_numpy(dtype=int),
        "temperature": gdf.temperature.to_numpy(dtype=float),
        "depth": gdf.new_depth.to_numpy(dtype=float),
    },
)
