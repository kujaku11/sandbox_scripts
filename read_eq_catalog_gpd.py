# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 10:34:28 2020

:author: Jared Peacock

:license: MIT

"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd
import geopandas as gpd

from pyevtk.hl import pointsToVTK

# =============================================================================

fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\utah\anss_eq_query.csv")
model_epsg = 32612
units = "km"
scale = 1
if units in ["km"]:
    scale = 1000

df = pd.read_csv(
    fn,
    # delimiter="\s+",
    header=0,
    usecols=["time", "latitude", "longitude", "depth", "mag"],
    # usecols=["time utc", "lat", "lon", "depth km", "magnitude"], # umatilla
    index_col=False,
    # skipfooter=1,
    engine="python",
)


gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.longitude, df.latitude)
)
gdf.crs = {"init": "epsg:4326"}
gdf.to_file(fn.parent.joinpath(f"{fn.stem}.shp"))

utm_gdf = gdf.to_crs(model_epsg)
utm_gdf["easting"] = utm_gdf.geometry.x
utm_gdf["northing"] = utm_gdf.geometry.y


pointsToVTK(
    fn.parent.joinpath(f"{fn.stem}_{units}_{model_epsg}").as_posix(),
    utm_gdf.easting.to_numpy() / scale,
    utm_gdf.northing.to_numpy() / scale,
    utm_gdf.depth.to_numpy() * -1,
    data={"mag": utm_gdf.mag.to_numpy(), "depth": utm_gdf.depth.to_numpy()},
)
