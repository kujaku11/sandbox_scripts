# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 20:20:37 2020

@author: jpeacock
"""

import glob
import geopandas as gpd
import fiona
from mtpy.utils import gis_tools
from shapely.geometry import Point
import pandas as pd
fiona.supported_drivers['kml'] = 'rw'
fiona.supported_drivers['KML'] = 'rw'
crs = {'init':'epsg:4326'}

txt_dir = r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\wannamaker_great_basin_locations"
cols =['station', 'zone', 'easting', 'northing', 'elevation']
types = [str, str, float, float, float]
dtypes = dict([(key, t) for key, t in zip(cols, types)])
df_dict=dict([(key, []) for key in cols])

for txt_fn in glob.glob('{0}\*.txt'.format(txt_dir)):
    try:
        df = pd.read_csv(txt_fn, skiprows=1, usecols=(0, 1, 2, 3, 4), 
                         names=cols, dtype=dtypes)
    except pd._libs.parsers.ParserError:
        df = pd.read_csv(txt_fn, skiprows=1, delimiter=r"\s+",
                         usecols=(0, 1, 2, 3, 4), 
                         names=cols,
                         dtype=dtypes)
        
    for col in cols:
        df_dict[col] += df[col].to_list()   

geometry = []
stations = {'ID':[],
            'elev':[],
            'lat':[],
            'lon':[]}

for index in range(len(df_dict['station'])):
    lon, lat = gis_tools.project_point_utm2ll(df_dict['easting'][index],
                                              df_dict['northing'][index],
                                              df_dict['zone'][index],
                                              datum='NAD83')
    geometry.append(Point(lon, lat))
    stations['ID'].append(df_dict['station'][index])
    stations['elev'].append(df_dict['elevation'][index])
    stations['lat'].append(lat)
    stations['lon'].append(lon)
    
gdf = gpd.GeoDataFrame(stations, crs=crs, geometry=geometry)
gdf.to_file(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\wannamaker.kml",
            driver='kml')    
gdf.to_file(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\wannamaker.shp",
            driver='ESRI Shapefile')