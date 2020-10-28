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

fn = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\mnp_earthquakes_scec.txt"
# fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\usgs_eq_catalog.csv"

df = pd.read_csv(fn, 
                 delimiter='\s+',
                 header=0,
                 usecols=['date', 'time', 'latitude', 'longitude', 'depth', 'mag'],
                 index_col=False,
                 #skipfooter=0,
                 engine='python')

df.columns = df.columns.str.lower()

df['geometry'] = df.apply(lambda z: Point(z.longitude, z.latitude), axis=1)
gdf = gpd.GeoDataFrame(df)
gdf.crs = {'init': 'epsg:4326'}

gdf.to_file(fn[:-4] + '.shp')

### Make vtk of earthquakes
model_east, model_north, model_utm = gis_tools.project_point_ll2utm(35.064399, -115.665516)

# make a new array with easting and northing
vtk_arr = np.zeros(df.shape[0], dtype=[('east', np.float),
                                       ('north', np.float),
                                       ('depth', np.float),
                                       ('mag', np.float)])

# compute easting and northing
for ii in range(df.shape[0]):
    e, n, z = gis_tools.project_point_ll2utm(df.latitude[ii], 
                                             df.longitude[ii])
    vtk_arr[ii]['east'] = (e-model_east)/1000.
    vtk_arr[ii]['north'] = (n-model_north)/1000.
    vtk_arr[ii]['depth'] = df.depth[ii]
    vtk_arr[ii]['mag'] = df.mag[ii]

   
pointsToVTK(fn[:-4], 
            vtk_arr['north'].copy(),
            vtk_arr['east'].copy(),
            vtk_arr['depth'].copy(),
            data={'mag':vtk_arr['mag'].copy(), 'depth':vtk_arr['depth'].copy()})


# # Write file
# fiona.Env()
# gdf.to_file(fn[:-4] + '.kml', driver='KML')
