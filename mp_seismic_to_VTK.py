# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 17:28:04 2014

@author: jpeacock
"""

import os
from evtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.latlongutmconversion as utm2ll

sfn = r"/mnt/hgfs/jpeacock/Documents/MountainPass/Maps/MountainPass_GIS/southern_california_earthquake_locations_crop.txt"
mc_lat = 35.464
mc_lon = -115.472

zone, east_0, north_0 = utm2ll.LLtoUTM(23, mc_lat, mc_lon)

s_array = np.loadtxt(sfn, delimiter=',', 
                     dtype = [('year', np.float),
                              ('month', np.float),
                              ('day', np.float),
                              ('hour', np.float),
                              ('minute', np.float),
                              ('second', np.float),
                              ('lat', np.float),
                              ('lon', np.float),
                              ('depth', np.float),
                              ('mag', np.float)],
                     skiprows=1)
                  
east = np.zeros(s_array.shape[0])
north = np.zeros(s_array.shape[0])

for ii, ss in enumerate(s_array):
    zz, ee, nn = utm2ll.LLtoUTM(23, ss['lat'], ss['lon'])
    east[ii] = (ee-east_0)/1000.
    north[ii] = (nn-north_0)/1000.


x = north.copy()
y = east.copy()
z = s_array['depth'].copy()
mag = s_array['mag'].copy()
year = s_array['year'].copy()


for xx, yy, zz, mm in zip(x[0:10], y[0:10], z[0:10], mag[0:10]):
    print 'N={0:.2f}, E={1:.2f}, Z={2:.2f}, M={3:.2f}'.format(xx, yy, zz, mm)
    
pointsToVTK(r"/home/jpeacock/Documents/mp_eq_locations", x, y, z, 
            data={'mag':mag, 'depth':z, 'year':year})
            


