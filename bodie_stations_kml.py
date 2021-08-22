# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 16:20:52 2016

@author: jpeacock
"""

import simplekml as skml

fn = r"d:\Peacock\MTData\LV\Bodie-Aurora-MT-stations.txt"

with open(fn, "r") as fid:
    lines = fid.readlines()

kml_obj = skml.Kml()

for line in lines[2:]:
    line_list = line.strip().split()
    name = line_list[0].strip()
    lat = float(line_list[1].strip()[1:])
    lon = -float(line_list[2].strip()[1:])

    kml_obj.newpoint(name=name, coords=[(lon, lat, 0.0)])

kml_obj.save(r"d:\Peacock\MTData\LV\Bodie-Aurora-MT-stations.kml")
