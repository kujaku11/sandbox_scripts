# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:05:45 2014

@author: jpeacock
"""

from evtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.latlongutmconversion as utm2ll

#---------------------------------------------------
#sfn = r"/home/jpeacock/Documents/EarthquakeLocations_DD.txt"
#sfn = r"/mnt/hgfs/jpeacock/Documents/LV/shelly_2015_mm_eq.txt"
sfn = r"c:\Users\jpeacock\Documents\LV\shelly_2015_mm_eq.txt"

len_file = 6211

sfid = file(sfn, 'r')
lines = sfid.readlines()

x = np.zeros(len_file)
y = np.zeros(len_file)
z = np.zeros(len_file)

read_line = 0
east_0 = 336800.00
north_0 = 4167510.00

for sline in lines[14:]:
    slst = sline.strip().split()
    lat = float(slst[6])
    lon = float(slst[7])
    depth = float(slst[8])
    
    zone, east, north = utm2ll.LLtoUTM(23, lat, lon)
    x[read_line] = (east-east_0)/1000.
    y[read_line] = (north-north_0)/1000.
    z[read_line] = depth
    read_line += 1
    
    
    
sfid.close()


    
pointsToVTK(r"c:\Users\jpeacock\Documents\LV\lv_3d_models\shelly_2015_mm_eq_lcv", y, x, z, 
            data={'depth':z})
