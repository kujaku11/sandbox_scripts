# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 10:40:47 2014

@author: jpeacock-pr
"""

import simplekml as skml
import os
import pyproj
csv_fn = r"c:\Users\jpeacock\Downloads\Bodie-Aurora-MT-stations.txt"

with open(csv_fn, 'r') as fid:
    csv_lines = fid.readlines()

                    

kml_obj = skml.Kml()

p_nad27 = pyproj.Proj(init='epsg:4267')
p_wgs84 = pyproj.Proj(init='epsg:4326')

for ii, line in enumerate(csv_lines[2:]):
    csv_list = line.strip().split()
    if len(csv_list) < 3:
        break
    csv_list = [cc.strip() for cc in csv_list]
#    station = 'HF{0:02}'.format(int(csv_list[0].split()[-1]))
    station = 'BR{0}'.format(csv_list[0])
    lon_27 = -1*float(csv_list[2][1:])
    lat_27 = float(csv_list[1][1:])
    
    lon_84, lat_84 = pyproj.transform(p_nad27, p_wgs84, lon_27, lat_27)
    pnt = kml_obj.newpoint(name=station, 
                           coords=[(lon_84, lat_84, 0.0)])
    pnt.style.labelstyle.color = skml.Color.white
    pnt.style.labelstyle.scale = .8
    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/dir_60.png'
    pnt.style.iconstyle.scale = .8

#kml_obj.save(csv_fn[:-4]+'.kml')
kml_obj.save(os.path.join(os.path.dirname(csv_fn), 
                          'br_mt_sites_2016.kml'))
    
            
            
