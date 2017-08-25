# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:05:45 2014

@author: jpeacock
"""

from evtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.gis_tools as gis_tools
import simplekml as skml

#---------------------------------------------------
sfn = r"c:\Users\jpeacock\Documents\NCDEC_DD_EQ_catalog_small.csv"
model_center = (514912.46, 4298145.35)

s_array = np.loadtxt(sfn, delimiter=',', 
                     dtype = [('lat', np.float),
                              ('lon', np.float),
                              ('depth', np.float),
                              ('mag', np.float)],
                     skiprows=1)

# crop out only the earthquakes in the desired area
s_array = s_array[np.where((s_array['lat'] <= 38.90) & (s_array['lat'] >=38.75))]
s_array = s_array[np.where((s_array['lon'] >= -122.92) & (s_array['lon']<=-122.72))]

# make a new array with easting and northing
vtk_arr = np.zeros_like(s_array, dtype=[('east', np.float),
                                        ('north', np.float),
                                        ('depth', np.float),
                                        ('mag', np.float)])

# compute easting and northing
for ii in range(s_array.shape[0]):
    e, n, z = gis_tools.project_point_ll2utm(s_array[ii]['lat'], 
                                             s_array[ii]['lon'])
    vtk_arr[ii]['east'] = (e-model_center[0])/1000.
    vtk_arr[ii]['north'] = (n-model_center[1])/1000.
    vtk_arr[ii]['depth'] = s_array[ii]['depth']
    vtk_arr[ii]['mag'] = s_array[ii]['mag']

   
pointsToVTK(r"c:\Users\jpeacock\Documents\ClearLake\EQ_DD_locations", 
            vtk_arr['north'],
            vtk_arr['east'],
            vtk_arr['depth'],
            data={'mag':vtk_arr['mag'], 'depth':vtk_arr['depth']})

# write kml file to check the accuracy
kml = skml.Kml()
for s_arr in s_array[np.arange(0, s_array.shape[0], 5)]:
    pnt = kml.newpoint(coords=[(s_arr['lon'], s_arr['lat'])])
    
kml.save(r"c:\Users\jpeacock\Documents\ClearLake\EQ_DD_locations.kml")

# write text file
txt_lines = ['ID,lat,lon,depth,mag']
for ii, s_arr in enumerate(s_array):
    txt_lines.append('{0},{1:.6f},{2:.6f},{3:.2f},{4:.2f}'.format(ii,
                                                          s_arr['lat'],
                                                          s_arr['lon'],
                                                          s_arr['depth'],
                                                          s_arr['mag']))
                                                          
with open(r"c:\Users\jpeacock\Documents\ClearLake\EQ_DD_locations.csv", 'w') as fid:
    fid.write('\n'.join(txt_lines))
                                                        