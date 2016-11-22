# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 16:48:16 2016

@author: jpeacock
"""

import numpy as np
import os

bb_conv_fn = r"c:\Users\jpeacock\Documents\ShanesBugs\BBConv.txt"

with open(bb_conv_fn, 'r') as fid:
    lines = fid.readlines()
    
data = []
for line in lines:
    line_list = line.strip().split()
    line_list = [float(value) for value in line_list]
    line_list[0] = 10**line_list[0]
    data.append(line_list)
    
data = np.array(data)
np.savetxt(os.path.join(os.path.dirname(bb_conv_fn), 'bb_conv.csv'), data,
           delimiter=',', fmt='%.5e')