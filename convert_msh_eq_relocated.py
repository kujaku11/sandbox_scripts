# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 11:45:05 2016

@author: jpeacock
"""


import os
from evtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.latlongutmconversion as utm2ll
import pandas as pd

msh_eq_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\pnsn_relocations_faults_2km_north.csv"

# model center
east_0 = 555703.0 - 253
north_0 = 5132626.0 + 26

with open(msh_eq_fn, "r") as fid:
    lines = fid.readlines()

eq_arr = np.zeros(
    len(lines) - 1,
    dtype=(
        [
            ("depth", np.float),
            ("east", np.float),
            ("north", np.float),
            ("mag", np.float),
        ]
    ),
)

eq_df = pd.read_csv(msh_eq_fn)

for ii in range(eq_df.shape[0]):
    eq = eq_df.iloc[ii]
    zone, east, north = utm2ll.LLtoUTM(23, eq.LATITUDE_D, eq.LONGITUDE_)
    eq_arr[ii]["east"] = (east - east_0) / 1000
    eq_arr[ii]["north"] = (north - north_0) / 1000
    eq_arr[ii]["depth"] = eq.EARTHQUA_1
    eq_arr[ii]["mag"] = eq.EARTHQUA_2

pointsToVTK(
    msh_eq_fn[:-4],
    eq_arr["north"],
    eq_arr["east"],
    eq_arr["depth"],
    data={"depth": eq_arr["depth"], "magnitude": eq_arr["mag"]},
)
