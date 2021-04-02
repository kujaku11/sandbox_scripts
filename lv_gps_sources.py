# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 14:42:07 2016

@author: jpeacock
"""

import mtpy.utils.latlongutmconversion as utm2ll
import pandas as pd

# model center:
east_0 = 336720
north_0 = 4167510

### --> gps Source locations
# Newman 2009
feng_09 = {"lat": 37.678, "lon": -118.930, "depth": 6.0, "name": "Feng_2009"}

# Langbein 1995
lb_95_01 = {"lat": 37.6869, "lon": -118.9150, "depth": 5.5, "name": "langbein_1995"}
lb_95_02 = {"lat": 37.6325, "lon": -118.9353, "depth": 13, "name": "langbein_1995"}

battaglia_03 = {"lat": 37.67856, "lon": -119.0164, "depth": 6, "name": "battaglia_2003"}
mb_15 = {"lat": 37.67852, "lon": -118.914, "depth": 7, "name": "montgomery_brown_2015"}

df = pd.DataFrame()

line_list = []
for gps_dict in [feng_09, lb_95_01, lb_95_02, battaglia_03, mb_15]:
    zone, east, north = utm2ll.LLtoUTM(23, gps_dict["lat"], gps_dict["lon"])
    gps_east = (east - east_0) / 1000.0
    gps_north = (north - north_0) / 1000.0
    gps_dict["model_east"] = gps_east
    gps_dict["model_north"] = gps_north

    line = "{0} center: {1:.2f} E, {2:.2f} N, Depth {3:.1f}".format(
        gps_dict["name"], gps_east, gps_north, gps_dict["depth"]
    )

    if len(line_list) == 0:
        line_list.append(",".join([key for key in sorted(gps_dict.keys())]))
    line_str = ["{0}".format(gps_dict[key]) for key in sorted(gps_dict.keys())]
    line_list.append(",".join(line_str))

    print(line)

with open(
    r"c:\Users\jpeacock\Documents\LV\lv_3d_models\inflation_locations.csv", "w"
) as fid:
    fid.write("\n".join(line_list))
