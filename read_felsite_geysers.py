# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 13:33:57 2019

@author: jpeacock
"""

import pandas as pd
import numpy as np
from pyevtk.hl import pointsToVTK
from mtpy.utils import gis_tools


fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\Top_Felsite_Points_WGS84.csv"

model_center = (38.831979, -122.828190)
model_east, model_north, zone = gis_tools.project_point_ll2utm(38.831979,
                                                               -122.828190,
                                                               epsg=32610)

df = pd.read_csv(fn, 
                 names=['lat', 'lon', 'elev'], 
                 usecols=[0, 1, 2],
                 skiprows=1,
                 dtype={'lat':np.float,
                        'lon':np.float,
                        'elev':np.float})

east, north, zone = gis_tools.project_points_ll2utm(df.lat.to_numpy(),
                                                    df.lon.to_numpy(),
                                                    epsg=32610)

y = (east - model_east) / 1000
x = (north - model_north) / 1000
z = (df.elev.to_numpy()*.3048) / 1000

pointsToVTK(fn[:-4],
            x, y, z, {'depth':z})

df_new = pd.DataFrame({'northing':x, 
                       'easting':y,
                       'depth':z})
df_new.to_csv(fn[:-4] + '_mc.csv', index=False)