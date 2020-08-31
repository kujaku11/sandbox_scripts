# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 10:34:28 2020

:author: Jared Peacock

:license: MIT

"""

import pandas as pd
import geopandas as gpd
import fiona
from shapely.geometry import Point

gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'


fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\usgs_eq_catalog.csv"

df = pd.read_csv(fn, 
                 delimiter=',',
                 header=0,
                 usecols=['time', 'latitude', 'longitude', 'depth', 'mag'],
                 index_col=False,
                 skipfooter=1,
                 engine='python')

df.columns = df.columns.str.lower()

df['geometry'] = df.apply(lambda z: Point(z.longitude, z.latitude), axis=1)
gdf = gpd.GeoDataFrame(df)

gdf.to_file(fn[:-4] + '.shp')

# Write file
fiona.Env()
gdf.to_file(fn[:-4] + '.kml', driver='KML')
