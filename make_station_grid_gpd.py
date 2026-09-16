# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 12:02:18 2022

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import numpy as np
import geopandas as gpd
from pyproj import CRS, Transformer
from shapely.geometry import Point

import fiona

fiona.drvsupport.supported_drivers["KML"] = "rw"
fiona.drvsupport.supported_drivers["kml"] = "rw"
fiona.drvsupport.supported_drivers["libkml"] = (
    "rw"  # enable KML support which is disabled by default
)
fiona.drvsupport.supported_drivers["LIBKML"] = (
    "rw"  # enable KML support which is disabled by default
)

# =============================================================================
save_shp = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GRIP\Alaska\akmt_proposed_2026.shp")

# Clayton Valley
# bbox = {"latitude": np.array([37.3679476,  38.5198050]),
#         "longitude": np.array([-118.4653828, -117.1159312])}

# # Battle Mountain
# bbox = {
#     "latitude": np.array([40.4074376, 40.6363425]),
#     "longitude": np.array([-117.0384026, -116.7590040]),
# }

# # Newberry
# bbox = {
#     "latitude": np.array([43.6, 43.85]),
#     "longitude": np.array([-121.42, -120.89]),
# }

### AKMT
bbox = {
    "latitude": np.array([61.4, 66.3]),
    "longitude": np.array([-168, -141]),
}

spacing = 30000
station = "akmt"
rotation_angle = 0
rcos = np.cos(np.deg2rad(rotation_angle))
rsin = np.sin(np.deg2rad(rotation_angle))

wgs84_crs = CRS.from_epsg(4326)
utm_crs = CRS.from_epsg(32606)

proj = Transformer.from_crs(wgs84_crs, utm_crs)
rev_proj = Transformer.from_crs(utm_crs, wgs84_crs)

ll = np.round(
    proj.transform(bbox["latitude"].min(), bbox["longitude"].min()), 0
)
ur = np.round(
    proj.transform(bbox["latitude"].max(), bbox["longitude"].max()), 0
)

x = np.linspace(ll[0], ur[0], int((ur[0] - ll[0]) / spacing))
y = np.linspace(ll[1], ur[1], int((ur[1] - ll[1]) / spacing))

count = 0
geometry = []
entry = {
    "station": [],
    "easting": [],
    "northing": [],
    "latitude": [],
    "longitude": [],
}
for xx in x:
    for yy in y:
        # if rotation_angle != 0:
        #     xx = xx * rcos - yy * rsin
        #     yy = xx * rsin + yy * rcos

        entry["station"].append(f"{station}{count:03}")
        entry["easting"].append(xx)
        entry["northing"].append(yy)
        lat, lon = rev_proj.transform(xx, yy)
        entry["latitude"].append(lat)
        entry["longitude"].append(lon)

        geometry.append(Point(lon, lat))
        count += 1

print(f"Total number of stations: {count}")

gdf = gpd.GeoDataFrame(entry, crs=wgs84_crs, geometry=geometry)
gdf.to_file(save_shp)

gdf = gdf.rename(columns={"station": "name"})
# gdf["name"] = [f"ld{x:03}" for x in range(len(gdf.name))]
gdf = gdf.to_crs(epsg=4326)
gdf.to_file(save_shp.parent.joinpath(f"{save_shp.stem}.kml"), driver="kml")
