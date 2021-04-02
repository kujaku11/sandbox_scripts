# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 13:33:57 2019

@author: jpeacock
"""

import pandas as pd
from pyevtk.hl import pointsToVTK
from mtpy.utils import gis_tools

fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\tos_points.txt"

model_north, model_east, zone = gis_tools.project_point_ll2utm(
    38.831979, -122.828190, epsg=32610
)

df = pd.read_csv(fn)

y = -1 * (model_north - df.X.to_numpy()) / 1000
x = -1 * (model_east - df.Y.to_numpy()) / 1000
z = -1 * (df.Elevation.to_numpy() * 0.3048) / 1000

pointsToVTK(fn[:-4], x, y, z, {"depth": z})

df_new = pd.DataFrame({"northing": x, "easting": y, "depth": z})
df_new.to_csv(fn[:-4] + "_mc.csv", index=False)
