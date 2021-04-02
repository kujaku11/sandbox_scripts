# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:05:45 2014

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pyevtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.gis_tools as gis_tools
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


# =============================================================================
# Parameters
# =============================================================================
sfn = r"C:\Users\jpeacock\OneDrive - DOI\MountainPass\gis\kml_files\mnp_earthquakes.csv"


model_center = (35.488658, -115.494148)
# model_east, model_north, model_zone = gis_tools.project_point_ll2utm(model_center[0],
#                                                                     model_center[1])
model_zone, model_east, model_north = gis_tools.ll_to_utm(
    23, model_center[0], model_center[1]
)


df = pd.read_csv(sfn, sep="\s+", skiprows=2, skipfooter=4, index_col=False)
df.columns = df.columns.str.lower()

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
    #    e, n, z = gis_tools.project_point_ll2utm(df.lat[ii],
    #                                             df.lon[ii])
    z, e, n = gis_tools.ll_to_utm(23, df.lat[ii], df.lon[ii])
    vtk_arr[ii]["east"] = (e - model_east) / 1000.0
    vtk_arr[ii]["north"] = (n - model_north) / 1000.0
    vtk_arr[ii]["depth"] = df.depth[ii]
    vtk_arr[ii]["mag"] = df.mag[ii]


pointsToVTK(
    r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\paraview_files\mp_eq",
    vtk_arr["north"].copy(),
    vtk_arr["east"].copy(),
    vtk_arr["depth"].copy(),
    data={"depth": vtk_arr["depth"].copy(), "mag": vtk_arr["mag"].copy()},
)

## write kml file to check the accuracy
# kml = skml.Kml()
# for ss in np.arange(0, df.shape[0], 5):
#    pnt = kml.newpoint(coords=[(df.lon[ss], df.lat[ss])])
#
# kml.save(r"c:\Users\jpeacock\Documents\MountainPass\MusicValley\mv_eq_locations.kml")

#### write shape file
point_geometry = [Point(x, y) for x, y in zip(df.lon, df.lat)]
datum = {"init": "epsg:4326"}

geo_df = gpd.GeoDataFrame(
    df.drop(["lat", "lon"], axis=1), crs=datum, geometry=point_geometry
)
geo_df.to_file(r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\gis\mv_eq_locations.shp")
