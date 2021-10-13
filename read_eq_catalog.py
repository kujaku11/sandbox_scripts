# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 10:34:28 2020

:author: Jared Peacock

:license: MIT

"""

import pandas as pd
import numpy as np
import geopandas as gpd

# import fiona
from shapely.geometry import Point
from pyevtk.hl import pointsToVTK
from mtpy.utils import gis_tools

fn = r"C:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\ncedc_eq.txt"
# fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\pnsn_event_export_20201201.csv"

df = pd.read_csv(
    fn,
    # delimiter="\s+",
    header=0,
    usecols=["datetime", "latitude", "longitude", "depth", "magnitude"],
    # usecols=["time utc", "lat", "lon", "depth km", "magnitude"], # umatilla
    index_col=False,
    # skipfooter=1,
    engine="python",
)

df.columns = df.columns.str.lower()
# df.rename(
#     columns={"lat": "latitude", "lon": "longitude", "depth km": "depth"}, inplace=True
# )
# Clear lake region
df = df.loc[
    (df.latitude >= 38.6)
    & (df.latitude <= 39.35)
    & (df.longitude >= -123.2)
    & (df.longitude <= -122.33)
]

df["geometry"] = df.apply(lambda z: Point(z.longitude, z.latitude), axis=1)
gdf = gpd.GeoDataFrame(df)
gdf.crs = {"init": "epsg:4326"}

gdf.to_file(fn[:-4] + ".shp")

### Make vtk of earthquakes
# model_east, model_north, model_utm = gis_tools.project_point_ll2utm(
#     39.556431, -119.800694
# )
# Umatilla
# model_east, model_north, model_utm = gis_tools.project_point_ll2utm(
#     45.650594, -118.562997
# )

# Clear Lake
model_east, model_north, model_utm = gis_tools.project_point_ll2utm(
    38.987645, -122.751369
)

# make a new array with easting and northing
vtk_arr = np.zeros(
    df.shape[0],
    dtype=[
        ("east", np.float),
        ("north", np.float),
        ("depth", np.float),
        ("mag", np.float),
    ],
)

# compute easting and northing
for ii in range(df.shape[0]):
    e, n, z = gis_tools.project_point_ll2utm(
        df.latitude.iloc[ii], df.longitude.iloc[ii], utm_zone=model_utm
    )
    vtk_arr[ii]["east"] = (e - model_east) / 1000.0
    vtk_arr[ii]["north"] = (n - model_north) / 1000.0
    vtk_arr[ii]["depth"] = df.depth.iloc[ii]
    vtk_arr[ii]["mag"] = df.magnitude.iloc[ii]


pointsToVTK(
    f"{fn[:-4]}_clearlake",
    vtk_arr["north"].copy(),
    vtk_arr["east"].copy(),
    vtk_arr["depth"].copy(),
    data={"mag": vtk_arr["mag"].copy(), "depth": vtk_arr["depth"].copy()},
)


# # Write file
# fiona.Env()
# gdf.to_file(fn[:-4] + '.kml', driver='KML')
