# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 16:31:19 2016

@author: jpeacock
"""

import numpy as np
import evtk.hl as a2vtk
import mtpy.utils.latlongutmconversion as ll2utm

# lin_fn = r"/mnt/hgfs/jpeacock/Google Drive/LV/2013_lin_relocated_eq.dat"
lin_fn = r"C:\Users\jpeacock\Documents\LV\2013_lin_relocated_eq.dat"

fid = file(lin_fn, "r")
lines = fid.readlines()
fid.close()

line_arr = np.array(
    [np.array(line.strip().split(), dtype=np.float) for line in lines[0].split("le")]
)

x = np.zeros(line_arr.shape[0])
y = np.zeros(line_arr.shape[0])
z = np.zeros(line_arr.shape[0])
mag = np.zeros(line_arr.shape[0])

# east_0 = 334460.0
# north_0 = 4173370.0
east_0 = 336800.0
north_0 = 4167525.0

for ii, l_arr in enumerate(line_arr[:-1]):
    lat = float(l_arr[7])
    lon = float(l_arr[8])
    depth = float(l_arr[9])
    mag[ii] = float(l_arr[10])

    zone, east, north = ll2utm.LLtoUTM(23, lat, lon)
    x[ii] = (east - east_0) / 1000.0
    y[ii] = (north - north_0) / 1000.0
    z[ii] = depth + 3

a2vtk.pointsToVTK(
    r"C:\Users\jpeacock\Documents\LV\lv_3d_models\2013_lin_relocated_eq",
    y,
    x,
    z,
    data={"depth": z, "magnitude": mag},
)
