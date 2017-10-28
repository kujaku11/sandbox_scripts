# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 11:56:06 2017

@author: jpeacock
"""

import os

dir_path = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03\depth_slices"

fn_list = [os.path.join(dir_path, fn) for fn in os.listdir(dir_path) 
            if fn.endswith('.tif')]

for fn in fn_list:
    depth = '{0:.0f}'.format(float(os.path.basename(fn).split('_')[1])-1260.00)
    depth = depth.replace('-', 'm')
    os.rename(fn, 
              os.path.join(dir_path, 'Geysers_mt_{0}m_WGS84.tif'.format(depth)))
    