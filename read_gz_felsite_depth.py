# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 11:10:43 2019

@author: jpeacock
"""

import pandas as pd
from mtpy.utils import gis_tools
#import vtk

fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\Top_Felsite_Points_WGS84.csv"

df = pd.read_csv(fn, delimiter=',', 
                 usecols=[0, 1, 2],
                 names=['lat', 'lon', 'depth'], skiprows=1)