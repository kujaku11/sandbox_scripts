# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:05:45 2014

@author: jpeacock
"""

from evtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.latlongutmconversion as utm2ll

#---------------------------------------------------
#sfn = r"c:\Users\jpeacock\Documents\LVEarthquakeLocations_lldm.csv"
sfn = r"c:\Users\jpeacock\Documents\MonoBasin\EQ_DD_locations.csv"

#save_sfn = sfn[:-4]+'_lldm.csv'
#sfid = file(save_sfn, 'w')
#sfid.writelines(line_list)
#sfid.close()


#east_0 = 336800.
#north_0 = 4167510.0
east_0 = 337350.-1200
north_0 = 4178250.0

s_array = np.loadtxt(sfn, delimiter=',', 
                     dtype = [('lat', np.float),
                              ('lon', np.float),
                              ('depth', np.float),
                              ('mag', np.float)],
                     skiprows=78,
                     usecols=(1, 2, 3, 8))

#zone0, east_0, north_0 = utm2ll.LLtoUTM(23, s_array['lat'].mean(), 
#                                        s_array['lon'].mean()) 


s_array = s_array[np.where((s_array['lat']<=38.0) & (s_array['lat']>=37.50))]
s_array = s_array[np.where((s_array['lon']>=-119.15) & (s_array['lon']<=-118.6))]
                                        
#print east_0, north_0
east = np.zeros(s_array.shape[0])
north = np.zeros(s_array.shape[0])

depth = []
mag = []


for ii, ss in enumerate(s_array):
    zz, ee, nn = utm2ll.LLtoUTM(23, ss['lat'], ss['lon'])
    east[ii] = (ee-east_0)/1000.
    north[ii] = (nn-north_0)/1000.

x = north.copy()
y = east.copy()
z = s_array['depth'].copy()
mag = s_array['mag'].copy()

    
pointsToVTK(r"c:\Users\jpeacock\Documents\LV\EQ_DD_locations_lvc_big", x, y, z, 
            data={'mag':mag, 'depth':z})
