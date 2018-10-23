# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:05:45 2014

@author: jpeacock
"""

from evtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.gis_tools as gis_tools
import simplekml as skml
import pandas as pd

#---------------------------------------------------
#sfn = r"c:\Users\jpeacock\Documents\NCDEC_DD_EQ_catalog_small.csv"
sfn = r"C:\Users\jpeacock\Documents\ClearLake\ncedc_eq_catalog_dd.csv"
model_center = (514912.46, 4298145.35)

df = pd.read_csv(sfn)

#s_array = np.loadtxt(sfn, delimiter=',', 
#                     dtype = [('lat', np.float),
#                              ('lon', np.float),
#                              ('depth', np.float),
#                              ('mag', np.float)],
#                     skiprows=1)
#
## crop out only the earthquakes in the desired area
#s_array = s_array[np.where((s_array['lat'] <= 38.90) & (s_array['lat'] >=38.75))]
#s_array = s_array[np.where((s_array['lon'] >= -122.92) & (s_array['lon']<=-122.72))]

# make a new array with easting and northing
vtk_arr = np.zeros(df.shape[0], dtype=[('east', np.float),
                                       ('north', np.float),
                                       ('depth', np.float),
                                       ('mag', np.float)])

# compute easting and northing
for ii in range(df.shape[0]):
    e, n, z = gis_tools.project_point_ll2utm(df.lat[ii], 
                                             df.lon[ii])
    vtk_arr[ii]['east'] = (e-model_center[0])/1000.
    vtk_arr[ii]['north'] = (n-model_center[1])/1000.
    vtk_arr[ii]['depth'] = df.depth[ii]
    vtk_arr[ii]['mag'] = df.mag[ii]

   
pointsToVTK(r"c:\Users\jpeacock\Documents\ClearLake\EQ_DD_locations", 
            vtk_arr['north'],
            vtk_arr['east'],
            vtk_arr['depth'],
            data={'mag':vtk_arr['mag'], 'depth':vtk_arr['depth']})

# write kml file to check the accuracy
kml = skml.Kml()
for ss in np.arange(0, df.shape[0], 5):
    pnt = kml.newpoint(coords=[(df.lon[ss], df.lat[ss])])
    
kml.save(r"c:\Users\jpeacock\Documents\ClearLake\EQ_DD_locations_2018.kml")

# write text file
df.to_csv(r"c:\Users\jpeacock\Documents\ClearLake\EQ_DD_locations_2018.csv",
          columns=['lat', 'lon', 'depth', 'mag'],
          index=True)
#txt_lines = ['ID,lat,lon,depth,mag']
#for ii in range(df.shape[0]):
#    txt_lines.append('{0},{1:.6f},{2:.6f},{3:.2f},{4:.2f}'.format(ii,
#                                                          s_arr['lat'],
#                                                          s_arr['lon'],
#                                                          s_arr['depth'],
#                                                          s_arr['mag']))
#                                                          
#with open(r"c:\Users\jpeacock\Documents\ClearLake\EQ_DD_locations_2018.csv", 'w') as fid:
#    fid.write('\n'.join(txt_lines))
                                                        