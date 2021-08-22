# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 10:40:47 2014

@author: jpeacock-pr
"""

import simplekml as skml
import os

csv_fn = r"c:\Users\jpeacock\Documents\Geothermal\MountainHome\MH-MT-2018.csv"

with open(csv_fn, "r") as fid:
    csv_lines = fid.readlines()


kml_obj = skml.Kml()


for ii, line in enumerate(csv_lines[1:]):
    csv_list = line.strip().split(",")
    if len(csv_list) < 3:
        break
    #    station = 'HF{0:02}'.format(int(csv_list[0].split()[-1]))
    station = "CM{0}".format(300 + ii + 1)
    lat = float(csv_list[3])
    lon = float(csv_list[2])
    pnt = kml_obj.newpoint(name=station, coords=[(lon, lat, 0.0)])
    pnt.style.labelstyle.color = skml.Color.white
    pnt.style.labelstyle.scale = 0.8
    pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/dir_60.png"
    pnt.style.iconstyle.scale = 0.8

# kml_obj.save(csv_fn[:-4]+'.kml')
kml_obj.save(os.path.join(os.path.dirname(csv_fn), "mh_mt_sites_2018.kml"))
