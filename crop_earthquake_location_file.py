# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 14:18:48 2015

@author: jpeacock-pr
"""

import os

lat_min = 37.4
lat_max = 38.5
lon_min = -119.3
lon_max = -118.5

fn = r"c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\GIS\EQ_DD_locations_lldm.csv"

n_fn = r"c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\GIS\EQ_DD_locations_lldm_crop.csv"

fid = file(fn, 'r')
nfid = file(n_fn, 'w')

header_line = fid.readline()
nfid.write('{0},{1},{2},{3},{4}\n'.format('lat', 'lon', 'depth', 'mag', 'ID'))

data_count = 1
line_count = 1
while line_count < 127489:
    line = [float(ll) for ll in fid.readline().strip().split(',')]
    if line[0] >= lat_min and line[0] <= lat_max:
        if line[1] >= lon_min and line[1] <= lon_max:
            nfid.write('{0:.5f},{1:.5f},{2:.3f},{3:.2f},{4:.0f}\n'.format(
            line[0], line[1], line[2], line[3], data_count))
            data_count +=1
    line_count +=1

fid.close()
nfid.close()            