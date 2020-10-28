# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 09:27:10 2014

@author: jpeacock-pr
"""

import os
import numpy as np
import mtpy.utils.latlongutmconversion as utm2ll
import simplekml as skml

# sfn = r"c:\Users\jpeacock-pr\Documents\MonoBasin\LP_and_BF_earthquake_locations.csv"
sfn = r"c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\EarthquakeLocations_DD.csv"

east_0 = 325090.62
north_0 = 4191809.70

# s_array = np.loadtxt(sfn, delimiter=',',
#                     dtype = [('year', np.float),
#                              ('month', np.float),
#                              ('day', np.float),
#                              ('lat', np.float),
#                              ('lon', np.float),
#                              ('depth', np.float),
#                              ('mag', np.float)],
#                     skiprows=1)
s_array = np.loadtxt(
    sfn,
    delimiter=",",
    dtype=[
        ("lat", np.float),
        ("lon", np.float),
        ("depth", np.float),
        ("mag", np.float),
    ],
    skiprows=1,
)


kml = skml.Kml()
for ii, ss in enumerate(s_array[np.arange(0, s_array.shape[0], 5)]):
    if ss["mag"] >= 1.0:
        kml.newpoint(name="", coords=[(ss["lon"], ss["lat"])])

kml.save(r"c:\Users\jpeacock-pr\Documents\ParaviewFiles\mb_mt\mb_eq_dd.kml")
