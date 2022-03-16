# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 10:50:54 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
import fiona
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"

# fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\Permits\2020.09.09_Geysers_Monitoring_MT_Stations_Lat_Long_East_North.csv"
fn = r"C:\Users\jpeacock\OneDrive - DOI\Geothermal\Battle_Mountain\battle_mountain_proposed_mt.txt"

df = pd.read_csv(fn, header=0, sep="\s+")

point_geometry = [Point(row.longitude, row.latitude) for row in df.itertuples()]

gdf = gpd.GeoDataFrame(df["station"], geometry=point_geometry)

with fiona.Env():
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # Might throw a WARNING - CPLE_NotSupported in b'dataset sample_out.kml does not support layer creation option ENCODING'
    gdf.to_file(fn[:-4] + ".kml", driver="KML")
