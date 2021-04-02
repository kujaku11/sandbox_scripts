# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:05:45 2014

@author: jpeacock
"""


import os
from evtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.gis_tools as gis_tools
import pandas as pd

# ---------------------------------------------------
# eq_fn = r"/mnt/hgfs/jpeacock/Documents/Geothermal/Washington/MSH/mshn_earthquake_locations_ll.csv"
eq_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\eq_psns_all_msh.csv"
sv_path = os.path.dirname(eq_fn)
# --------------------------------------

eq_df = pd.read_csv(eq_fn)

# model center
# east_0 = 555703.-253
# north_0 = 5132626.0+26

east_0 = 562012.0
north_0 = 5128858.0

x = np.zeros_like(eq_df.Lat)
y = np.zeros_like(eq_df.Lon)
for lat, lon, index in zip(eq_df.Lat, eq_df.Lon, range(x.size)):
    east, north, zone = gis_tools.project_point_ll2utm(lat, lon)
    x[index] = (east - east_0) / 1000.0
    y[index] = (north - north_0) / 1000.0

pointsToVTK(
    eq_fn[:-4] + "shz",
    y,
    x,
    np.array(eq_df.Depth),
    data={"depth": np.array(eq_df.Depth), "magnitude": np.array(eq_df.Magnitude)},
)
