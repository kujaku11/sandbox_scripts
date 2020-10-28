# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 11:10:43 2019

@author: jpeacock
"""

import pandas as pd
from mtpy.utils import gis_tools
from pyevtk.hl import pointsToVTK
import numpy as np

fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\Top_Felsite_Points_WGS84.csv"
model_center = (38.831979, -122.828190)

model_east, model_north, zone = gis_tools.project_point_ll2utm(
    model_center[0], model_center[1]
)
df = pd.read_csv(
    fn, delimiter=",", usecols=[0, 1, 2], names=["lat", "lon", "depth"], skiprows=1
)

east, north, zone = gis_tools.project_points_ll2utm(df.lat, df.lon)

x = (east - model_east) / 1000.0
y = (north - model_north) / 1000.0
z = (df.depth.to_numpy() / 3.25) / 1000.0

pointsToVTK(fn[:-4], y, x, z, {"depth": z})
