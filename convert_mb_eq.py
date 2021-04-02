# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:05:45 2014

@author: jpeacock
"""


import os
from evtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.latlongutmconversion as utm2ll
import pandas as pd

# ---------------------------------------------------
eq_fn = (
    r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\pnsn_mb_eq_catalog_2016.csv"
)
sv_path = os.path.dirname(eq_fn)
# --------------------------------------

eq_df = pd.read_csv(eq_fn)

# model center
east_0 = 596565.0
north_0 = 5397540.0

x = np.zeros_like(eq_df.Lat)
y = np.zeros_like(eq_df.Lon)
for lat, lon, index in zip(eq_df.Lat, eq_df.Lon, range(x.size)):
    zone, east, north = utm2ll.LLtoUTM(23, lat, lon)
    x[index] = (east - east_0) / 1000.0
    y[index] = (north - north_0) / 1000.0

pointsToVTK(
    eq_fn[:-4],
    y,
    x,
    np.array(eq_df.Depth_Km),
    data={"depth": np.array(eq_df.Depth_Km), "magnitude": np.array(eq_df.Magnitude)},
)
