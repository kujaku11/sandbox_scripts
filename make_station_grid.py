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

## Gabbs valley
ll_utm = {'zone':'11N', 
          'easting_min':394800.,
          'easting_max':402800.,
          'northing_min':4287500.,
          'northing_max':4296000.}

spacing_east = 1000.
spacing_north = 1000.
dx = 200

 

east_arr = np.arange(ll_utm['easting_min'], 
                     ll_utm['easting_max']+spacing_east,
                     spacing_east)
                     
north_arr = np.arange(ll_utm['northing_min'], 
                     ll_utm['northing_max']+spacing_east,
                     spacing_east)
                     
kml_fn = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\gabbs_valley_MT_preliminary_{0:.0f}m.kml".format(spacing_east)

kml_obj = skml.Kml()
count = 0
for ii, east in enumerate(east_arr):
    for jj, north in enumerate(north_arr):

        lat_ii, lon_jj = gis_tools.project_point_utm2ll(east, 
                                                        north, 
                                                        ll_utm['zone'])

        kml_obj.newpoint(name='GV{0:02}'.format(count),
                         coords=[(lon_jj, lat_ii)])
                         
        count += 1
                         
kml_obj.save(kml_fn)

print 'Number of stations: {0}'.format(count+1)