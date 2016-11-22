# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 10:38:18 2016

@author: jpeacock
"""

import simplekml as skml
import numpy as np
import os
import mtpy.utils.latlongutmconversion as ll2utm

###MSH north
#ll_utm = {'zone':'10T', 
#          'easting_min':550000.,
#          'easting_max':562000.,
#          'northing_max':5137000.,
#          'northing_min':5126400.}

#### MSH south
#ll_utm = {'zone':'10T', 
#          'easting_min':589700.,
#          'easting_max':600000.,
#          'northing_max':5403000.,
#          'northing_min':5388000.}
#
#spacing_east = 1500.
#spacing_north = 1500.

#### MSH south
#ll_utm = {'zone':'13S', 
#          'easting_min':387000.,
#          'easting_max':395000.,
#          'northing_max':3552000.,
#          'northing_min':3545000.}
#
#spacing_east = 2000.
#spacing_north = 1000.
#dx = 200
### clear lake south
#ll_utm = {'zone':'10S', 
#          'easting_min':512470.,
#          'easting_max':531800.,
#          'northing_min':4302600.,
#          'northing_max':4322900.}
ll_utm = {'zone':'11T', 
          'easting_min':364000.,
          'easting_max':392100.,
          'northing_min':5040000.,
          'northing_max':5068300.}

spacing_east = 3000.
spacing_north = 3000.
dx = 200

#center_east = (ll_utm['easting_max']+ll_utm['easting_min'])/2.
#center_north = (ll_utm['northing_max']+ll_utm['northing_min'])/2.
#
#east = float(center_east)
#north = float(center_north)
#count = 0
#
#east_list_p = [east]
#
#while east < ll_utm['easting_max']:
#    east += count*dx+spacing_east 
#    count += 1
#    east_list_p.append(east)
#    
#count = 1
#east_list_n = []
#east = float(center_east)
#
#while east > ll_utm['easting_min']:
#    east -= count*dx+spacing_east 
#    count += 1
#    east_list_n.append(east)
#
#east_arr = np.array(east_list_n[::-1]+east_list_p)    
#
#count = 0
#north_list_p = [north]
#north = float(center_north)
#
#while north < ll_utm['northing_max']:
#    north += count*dx+spacing_north 
#    count += 1
#    north_list_p.append(north)
#    
#count = 1
#north_list_n = []
#north = float(center_north)
#while north > ll_utm['northing_min']:
#    north -= count*dx+spacing_north 
#    count += 1
#    north_list_n.append(north)
#
#north_arr = np.array(north_list_n[::-1]+north_list_p) 

east_arr = np.arange(ll_utm['easting_min'], 
                     ll_utm['easting_max']+spacing_east,
                     spacing_east)
                     
north_arr = np.arange(ll_utm['northing_min'], 
                     ll_utm['northing_max']+spacing_east,
                     spacing_east)
                     
kml_fn = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\umatilla_MT_preliminary_{0:.0f}m.kml".format(spacing_east)

kml_obj = skml.Kml()
count = 0
for ii, east in enumerate(east_arr):
    for jj, north in enumerate(north_arr):
#        east += (-east_arr.shape[0]/2.+ii)*dx.
#        north += (-north_arr.shape[0]/2.+jj)*dx.
        lat_ii, lon_jj = ll2utm.UTMtoLL(23, north, east, ll_utm['zone'])
#        kml_obj.newpoint(name='CL{0}{1}'.format(ii, jj),
#                         coords=[(lon_jj, lat_ii)])
        kml_obj.newpoint(name='',
                         coords=[(lon_jj, lat_ii)])
                         
        count += 1
                         
kml_obj.save(kml_fn)

print 'Number of stations: {0}'.format(count+1)