# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 13:55:06 2018

@author: jpeacock
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point

csv_fn = r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\minerals\mrds.csv"

cols = [
    "site_name",
    "latitude",
    "longitude",
    "dep_id",
    "commod1",
    "commod2",
    "commod3",
    "dev_stat",
    "structure",
    "hrock_type",
    "ore",
]

exempt_list = [
    "ash",
    "cement rock",
    "clay",
    "construction",
    "crushed/broken",
    "dimension",
    "free",
    "fire clay (refractory)",
    "limestone",
    "metal",
    "sand and gravel",
    "stone",
    "water",
    "volcanic materials",
    "",
]

crs = {"init": "epsg:4326"}

df = pd.read_csv(csv_fn, usecols=cols, keep_default_na=False)
df.latitude.replace("", np.nan, inplace=True)
df.longitude.replace("", np.nan, inplace=True)

df.dropna(subset=["latitude", "longitude"], inplace=True)
df.latitude = df.latitude.astype(np.float)
df.longitude = df.longitude.astype(np.float)

# df = df[(df.latitude < 39.1) & (df.latitude > 38.5) &
#        (df.longitude < -117.75) & (df.longitude > -118.5)]
df = df[
    (df.latitude < 37.5)
    & (df.latitude > 31)
    & (df.longitude < -114)
    & (df.longitude > -124)
]
df = df.reset_index()

# get a list of the ore types
ore_list = []
for commod in df.commod1.astype(str):
    for ss in commod.split(","):
        ss = ss.strip().lower()
        if ss in exempt_list:
            continue
        ore_list.append(ss)

ore_list = sorted(list(set(ore_list)))
# add ore list onto data frame as falses
for ore in ore_list:
    df[ore] = 0
# df['resources'] = ''
for ii in range(df.shape[0]):
    site_ores = (
        df.loc[ii, "commod1"].lower().split(",")
        + df.loc[ii, "commod2"].lower().split(",")
        + df.loc[ii, "commod3"].lower().split(",")
    )
    #    site_ores = ','.join([ss.strip() for ss in site_ores if len(ss) > 2])
    #    df.at[ii, 'resources'] = site_ores
    for ore in ore_list:
        if ore in site_ores:
            df.at[ii, ore] = 1
df = df.reset_index()
# df.to_csv(r"c:\Users\jpeacock\Documents\ArcGIS\minerals\ores.csv",
#          index=False)

# df = pd.read_csv(r"c:\Users\jpeacock\Documents\ArcGIS\minerals\gabbs_ores.csv")
# points = [Point(x, y) for x, y in zip(df.longitude, df.latitude)]
# df = df.drop(['commod1', 'commod2', 'commod3', 'latitude', 'longitude'], axis=1)
df = df.rename(columns={"site_name": "site"})
df.site = df.site.astype(str)

for ore in ore_list:
    ore_df = df[["site", "latitude", "longitude", "dep_id", "dev_stat", ore]]
    ore_df = ore_df[ore_df[ore] == 1]
    ore_df = ore_df.reset_index()
    points = [Point(x, y) for x, y in zip(ore_df.longitude, ore_df.latitude)]
    ore_df = ore_df.drop(["latitude", "longitude"], axis=1)
    if ore_df.shape[0] == 0:
        continue
    gdf = gpd.GeoDataFrame(ore_df, crs=crs, geometry=points)
    gdf.to_file(
        r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\minerals\socal_{0}.shp".format(ore)
    )
