# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:05:45 2014

@author: jpeacock
"""

from evtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.latlongutmconversion as utm2ll

# ---------------------------------------------------
# sfn = r"/home/jpeacock/Documents/EarthquakeLocations_DD.txt"
sfn = r"c:\Users\jpeacock\Documents\LV\lv_2014_swarm_shelly.txt"

len_file = 8930

sfid = file(sfn, "r")

x = np.zeros(len_file)
y = np.zeros(len_file)
z = np.zeros(len_file)

read_line = 0
# original LV geothermal model
# east_0 = 334460.00
# north_0 = 4173370.00

# east_0 = 336720.
# north_0 = 4167510.0
east_0 = 336720.0
north_0 = 4167510.0

while read_line < len_file:
    sline = sfid.readline()
    slst = sline.strip().split()
    lat = float(slst[6])
    lon = float(slst[7])
    depth = float(slst[8])

    zone, east, north = utm2ll.LLtoUTM(23, lat, lon)
    x[read_line] = (east - east_0) / 1000.0
    y[read_line] = (north - north_0) / 1000.0
    z[read_line] = depth
    read_line += 1


sfid.close()

pointsToVTK(
    r"c:\Users\jpeacock\Documents\LV\lv_3d_models\lv_2014_swarm_locations_lvc",
    y,
    x,
    z,
    data={"depth": z},
)
