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

#---------------------------------------------------
#eq_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\pnsn_eq_catalog_20161014.csv"
eq_fn = r"c:\Users\jpeacock\Documents\iMush\eq_pnsn_events.csv"
sv_path = os.path.dirname(eq_fn)
#--------------------------------------

eq_df = pd.read_csv(eq_fn)

                  
# get only the earthquake information
eq_csv = eq_df[['Lat', 'Lon','Depth_Km', 'Magnitude']]
eq_csv.to_csv(r"c:\Users\jpeacock\Documents\iMush\pnsn_eq_catalog_ll.csv")

# model center
#east_0 = 564530.
#north_0 = 5105250.
east_0 = 574356
north_0 = 5144382.

x = np.zeros_like(eq_df.Lat)
y = np.zeros_like(eq_df.Lon)
for lat, lon, index in zip(eq_df.Lat, eq_df.Lon, range(x.size)):
    zone, east, north = utm2ll.LLtoUTM(23, lat, lon)
    x[index] = (east-east_0)/1000.
    y[index] = (north-north_0)/1000.
    
pointsToVTK(eq_fn[:-4], y, x, np.array(eq_df.Depth_Km), 
            data={'depth':np.array(eq_df.Depth_Km), 
                  'magnitude':np.array(eq_df.Magnitude)})