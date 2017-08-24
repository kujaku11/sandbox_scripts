# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 15:20:31 2017

@author: jpeacock
"""

import numpy as np
import mtpy.utils.gis_tools as gis_tools
from evtk.hl import pointsToVTK

sfn = r"C:\Users\jpeacock\Documents\ClearLake\geyser_egs_eq.txt"
model_center = (514912.46, 4298145.35)

s_array = np.loadtxt(sfn, 
                   delimiter=',',
                   dtype=[('lat', np.float),
                          ('lon', np.float),
                          ('depth', np.float),
                          ('mag', np.float)],
                   skiprows=14,
                   usecols=(1, 2, 3, 4))

# make a new array with easting and northing
vtk_arr = np.zeros_like(s_array, dtype=[('east', np.float),
                                        ('north', np.float),
                                        ('depth', np.float),
                                        ('mag', np.float)])
                                        
for ii, ss in enumerate(s_array):
    e, n, z = gis_tools.project_point_ll2utm(ss['lat'], ss['lon'])
    vtk_arr[ii]['east'] = (e-model_center[0])/1000.
    vtk_arr[ii]['north'] = (n-model_center[1])/1000.
    vtk_arr[ii]['depth'] = ss['depth']
    vtk_arr[ii]['mag'] = ss['mag']                      

pointsToVTK(r"c:\Users\jpeacock\Documents\ClearLake\egs_eq_locations", 
            vtk_arr['north'],
            vtk_arr['east'],
            vtk_arr['depth'],
            data={'mag':vtk_arr['mag'], 'depth':vtk_arr['depth']})

# write text file
txt_lines = ['ID,lat,lon,depth,mag']
for ii, s_arr in enumerate(s_array):
    txt_lines.append('{0},{1:.6f},{2:.6f},{3:.2f},{4:.2f}'.format(ii,
                                                          s_arr['lat'],
                                                          s_arr['lon'],
                                                          s_arr['depth'],
                                                          s_arr['mag']))
                                                          
with open(r"c:\Users\jpeacock\Documents\ClearLake\egs_eq_locations.csv", 'w') as fid:
    fid.write('\n'.join(txt_lines))