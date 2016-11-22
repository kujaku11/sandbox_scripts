# -*- coding: utf-8 -*-
"""
Created on Tue Jul 08 11:33:23 2014

@author: jpeacock-pr
"""

import numpy as np
import os
import mtpy.core.mt as mt
import matplotlib.pyplot as plt

edipath = r"c:\Users\jpeacock-pr\Documents\ShanesBugs\Jess\EDI_files"
edilst = [mt.MT(os.path.join(edipath, edi)) for edi in os.listdir(edipath)
          if edi.find('.edi') > 0]

def albers_transform(lat, lon, ref_lat=0.0, ref_lon=0.0, 
                     lat_1=0, lat_2=-60):
    """
    lat --> latitude of point in decimal degrees
    lon --> longitude of point in decimal degrees
    ref_lat --> reference latitude
    ref_lon --> reference longitude
    lat_1 --> lower bounds on latitude
    lat_2 --> upper bound on latitude
    """         
    
    n = .5*(np.sin(np.deg2rad(lat_1))+np.sin(np.deg2rad(lat_2)))
    theta = n*(lon-ref_lon)
    c = np.cos(np.deg2rad(lat_1))**2+2*n*np.sin(np.deg2rad(lat_1))
    rho = np.sqrt(c-2*n*np.sin(lat))/n
    rho_0 = np.sqrt(c-2*n*np.sin(np.deg2rad(ref_lat)))
    
    x = rho*np.sin(theta)
    y = rho_0-rho*np.cos(theta)
    
    return x, y
    
loc = np.zeros(len(edilst), dtype=[('east', np.float),
                                   ('north', np.float),
                                   ('lat', np.float),
                                   ('lon', np.float),
                                   ('new_east', np.float),
                                   ('new_north', np.float)])
for ii, mt_obj in enumerate(edilst):
    new_east, new_north = albers_transform(mt_obj.lat, mt_obj.lon)
    loc[ii]['east'] = mt_obj.east
    loc[ii]['north'] = mt_obj.north
    loc[ii]['new_east'] = new_east
    loc[ii]['new_north'] = new_north
    loc[ii]['lat'] = mt_obj.lat
    loc[ii]['lon'] = mt_obj.lon
    
fig = plt.figure(1)
ax1 = fig.add_subplot(3, 1, 1, aspect='equal')
ax2 = fig.add_subplot(3, 1, 2, aspect='equal')
ax3 = fig.add_subplot(3, 1, 3, aspect='equal')

ax1.scatter(loc['lon'], loc['lat'], marker = 'v')
ax2.scatter(loc['east'], loc['north'], marker = 'v')
ax3.scatter(loc['new_east'], loc['new_north'], marker='v')

plt.show()
    