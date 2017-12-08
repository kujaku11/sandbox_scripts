# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 10:38:18 2016

@author: jpeacock
"""

import simplekml as skml
import numpy as np
import mtpy.utils.gis_tools as gis_tools

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
#ll_utm = {'zone':'11T', 
#          'easting_min':364000.,
#          'easting_max':392100.,
#          'northing_min':5040000.,
#          'northing_max':5068300.}

### Gabbs valley
#ll_utm = {'zone':'11N', 
#          'easting_min':394800.,
#          'easting_max':402800.,
#          'northing_min':4287500.,
#          'northing_max':4296000.}
## Gabbs valley
ll_utm = {'lon_min':-118.0,
          'lon_max':-114.3,
          'lat_min':32.75,
          'lat_max':35.75}

spacing_east = 30./111.34
spacing_north = 20./111.34


 

lat_arr = np.arange(ll_utm['lat_min'], 
                     ll_utm['lat_max']+spacing_north,
                     spacing_north)
                     
lon_arr = np.arange(ll_utm['lon_min'], 
                     ll_utm['lon_max']+spacing_east,
                     spacing_east)
                     
kml_fn = r"c:\Users\jpeacock\Documents\MountainPass\mojave_{0:.0f}m.kml".format(spacing_east)

kml_obj = skml.Kml()
count = 0
for ii, lat_ii in enumerate(lat_arr):
    for jj, lon_jj in enumerate(lon_arr):

        kml_obj.newpoint(name='MJ{0:02}'.format(count),
                         coords=[(lon_jj, lat_ii)])
                         
        count += 1
                         
kml_obj.save(kml_fn)

print 'Number of stations: {0}'.format(count+1)