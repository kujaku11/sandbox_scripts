# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 17:49:36 2018

@author: jpeacock
"""

import mtpy.utils.array2raster as a2r
import numpy as np

# =============================================================================
# Inputs
# =============================================================================
mag_fn = r"c:\Users\jpeacock\Documents\ClearLake\GIS\CA_4168.xyz"

box_lat = np.array([38.7, 38.9])
box_lon = np.array([-122.95, -122.7])
# =============================================================================
# read mag file
# =============================================================================
mag_arr = np.loadtxt(mag_fn, 
                     usecols=(2, 3, 9, 10),
                     dtype={'names':('lon', 'lat', 'total', 'res'),
                            'formats':(np.float, np.float, np.float, np.float)})

x = np.array(sorted(list(set(mag_arr['lon']))))
y = np.array(sorted(list(set(mag_arr['lat']))))

x = x[np.where((x >= box_lon.min()) & (x <= box_lon.max()))]
y = y[np.where((y >= box_lat.min()) & (y <= box_lat.max()))]

res_arr = np.zeros((x.size, y.size))
total_arr = np.zeros((x.size, y.size))

for m_arr in mag_arr:
    
    if m_arr['lon'] >= box_lon.min() and m_arr['lon'] <= box_lon.max():
        if m_arr['lat'] >= box_lat.min() and m_arr['lat'] <= box_lat.max():
            x_index = np.where(x == m_arr['lon'])[0][0]
            y_index = np.where(y == m_arr['lat'])[0][0]
            
            res_arr[x_index, y_index] = m_arr['res']
            total_arr[x_index, y_index] = m_arr['total']
        else:
            continue
    
a2r.array2raster(r"c:\Users\jpeacock\Documents\ClearLake\GIS\mag_residual.tif",
                 (x.min(), y.min()),
                 11, 11,
                 res_arr)

a2r.array2raster(r"c:\Users\jpeacock\Documents\ClearLake\GIS\mag_total.tif",
                 (x.min(), y.min()),
                 11, 11,
                 total_arr)