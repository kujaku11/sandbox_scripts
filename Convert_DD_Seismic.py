# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:05:45 2014

@author: jpeacock
"""

from pyevtk.hl import pointsToVTK
import pandas as pd
import geopandas as gpd
from mtpy.core.mt_location import MTLocation

# ---------------------------------------------------
# sfn = r"c:\Users\jpeacock\Documents\LVEarthquakeLocations_lldm.csv"
sfn = r"c:\Users\jpeacock\OneDrive - DOI\LV\EarthquakeLocations_DD_lldm.csv"

bbox = ()

df = pd.read_csv(sfn)
df = df.loc[
    (df.lon >= -119.25)
    & (df.lon <= -118.5)
    & (df.lat >= 37.5)
    & (df.lat <= 38.35)
]


gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))
gdf.crs = "epsg:4326"
gdf = gdf.to_crs(epsg=32611)

center = MTLocation(longitude=-118.897992, latitude=37.914380)
center.utm_epsg = 32611


pointsToVTK(
    r"c:\Users\jpeacock\OneDrive - DOI\LV\eq_dd_large",
    (gdf.geometry.y - center.north).to_numpy(dtype=float) / 1000,
    (gdf.geometry.x - center.east).to_numpy(dtype=float) / 1000,
    gdf.depth.to_numpy(dtype=float) - 2.1,
    data={
        "mag": gdf.mag.to_numpy(dtype=float),
        "depth": gdf.depth.to_numpy(dtype=float),
    },
)
