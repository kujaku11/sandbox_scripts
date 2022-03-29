# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 15:27:16 2013

@author: jpeacock-pr
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import fiona

fiona.supported_drivers["KML"] = "rw"
# =============================================================================
# Inputs
# =============================================================================
kml_file = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\mnp_proposed_lp_mt_no_wilderness_2019.kml"
datum = {"init": "epsg:4326"}
stem = "mnp"
counter = 300

### new file names
txt_file = "{0}.txt".format(kml_file[:-4])
csv_file = "{0}.csv".format(kml_file[:-4])
shp_file = "{0}.shp".format(kml_file[:-4])
nkml_file = "{0}.kml".format(kml_file[:-4])
# ==============================================================================
# read in information from kml file
# ==============================================================================
with open(kml_file, "r") as kfid:
    klines = kfid.readlines()

df_dict = {"station": [], "lat": [], "lon": []}

ii = counter
for kline in klines:
    if kline.find("coordinates") > 0:
        klist = kline.strip().split(",")
        try:
            df_dict["lon"].append(float(klist[0].split(">")[1]))
            df_dict["lat"].append(float(klist[1].split("<")[0]))
            df_dict["station"].append("{0}{1:03}".format(stem, ii))
            ii += 1
        except ValueError:
            pass

df = pd.DataFrame(df_dict)

# write csv file
df.to_csv(csv_file, index=False)

# write shape file
gdf = gpd.GeoDataFrame(df, crs=datum,)
gdf["geometry"] = [Point(x[1]["lon"], x[1]["lat"]) for x in df.iterrows()]
gdf.to_file(shp_file)

# write kml file
gdf = gdf.drop(["lat", "lon"], axis=1)
gdf = gdf.rename(columns={"station": "name"})
gdf.to_file(nkml_file, driver="KML")
