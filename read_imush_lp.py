# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 12:17:50 2017

@author: jpeacock
"""

import numpy as np
import mtpy.utils.gis_tools as gis_tools
from evtk.hl import pointsToVTK

fn = r"c:\Users\jpeacock\Documents\iMush\DLP_Wes.txt"

lp_arr = np.loadtxt(fn, delimiter=',', skiprows=1, usecols=[0, 1, 2, 3],
                    dtype={'names':('lat', 'lon', 'depth', 'mag'),
                           'formats':(np.float, np.float, np.float, np.float)})

lines = ['lat,lon,east,north,depth,mag']
easting = np.zeros(lp_arr.size)
northing = np.zeros(lp_arr.size)
for kk, lp in enumerate(lp_arr):
    east, north, zone = gis_tools.project_point_ll2utm(float(lp['lat']),
                                                       float(lp['lon']))
    lines.append(','.join(['{0:.5f}'.format(ii) for ii in [lp['lat'],
                                                           lp['lon'],
                                                           east,
                                                           north,
                                                           lp['depth'],
                                                           lp['mag']]]))
    easting[kk] = east
    northing[kk] = north
    
with open(fn[:-4]+'_ew.txt', 'w') as fid:
    fid.write('\n'.join(lines))
    
# write vtk file
#pointsToVTK(fn[0:-4], 
#            (northing-5144510)/1000., 
#            (easting-573840)/1000.,
#            lp_arr['depth'],
#            data={'depth':lp_arr['depth'], 'mag':lp_arr['mag']})  
#  
# write vtk file shear zone
pointsToVTK(fn[0:-4]+'_shz', 
            (northing-5128858.)/1000., 
            (easting-562012.)/1000.,
            lp_arr['depth'],
            data={'depth':lp_arr['depth'], 'mag':lp_arr['mag']}) 