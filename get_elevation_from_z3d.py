# -*- coding: utf-8 -*-
"""
Created on Mon May 14 13:48:54 2018

@author: jpeacock
"""

import mtpy.usgs.zen as zen
import os

directory = r"d:\Peacock\MTData\Camas"
import pickle

info_dict = {}
#elevation_lines = ['station,elevation']
for folder in os.listdir(directory):
    if 'cm' in folder:
        f_path = os.path.join(directory, folder)
        fn_list = [os.path.join(f_path, fn) for fn in os.listdir(f_path) if
                   fn.endswith('Z3D')]
        z1 = zen.Zen3D(fn_list[0])
        z1.read_all_info()
        z1.station = z1.station.replace('mv', 'cm')
        info_dict[z1.station] = {}
        #elevation_lines.append('{0},{1:.2f}'.format(z1.station, z1.header.alt))
        info_dict[z1.station]['elev'] = z1.header.alt
        info_dict[z1.station]['zen_id'] = z1.header.box_number
        
#with open(os.path.join(directory, 'elevation.dat'), 'w') as fid:
#    fid.write('\n'.join(elevation_lines))
with open(os.path.join(directory, 'elevation.pkl'), 'w') as fid:
    pickle.dump(info_dict, fid)
