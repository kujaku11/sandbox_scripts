# -*- coding: utf-8 -*-
"""
Created on Wed May 17 19:38:19 2017

@author: jpeacock-pr
"""

from fastkml import kml

kml_fn = r"c:\Users\jpeacock-pr\Documents\MB_station_locations.kml"

with open(kml_fn, 'r') as fid:
    kml_str = fid.read()

k = kml.KML()
k.from_string(kml_str)

f = list(k.features())[0]

points = ['name,lat,lon,rms_200m,rms_3000m']
for m in f.features():
    point = []
    if 'mb' in m.name.lower():
        point.append(m.name.replace('b', ''))
        loc = m.geometry
        point.append('{0:.8f}'.format(loc.y))
        point.append('{0:.8f}'.format(loc.x))
        point.append(' ')
        point.append(' ')
        points.append(','.join(point))
        
csv_fn = kml_fn[0:-4]+'.csv'
with open(csv_fn, 'w') as fid:
    fid.write('\n'.join(points))
