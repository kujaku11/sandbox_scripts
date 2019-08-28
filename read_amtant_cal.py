# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import numpy as np
import pandas as pd

ant_fn = r"d:\Peacock\MTData\Ant_calibrations\antenna_20190411.cal"

with open(ant_fn, 'r') as fid:
    lines = fid.readlines()
    
ant_dict = {}
ff = 0
for line in lines:
    if 'antenna' in line.lower():
        f = 2*np.pi*float(line.split()[2].strip())
        ff += 1
    elif len(line.strip().split()) == 0:
        continue
    else:
        line_list = line.strip().split()
        ant = line_list[0]
        amp = float(line_list[1]) / 1000 ### to mV/nT
        phase = float(line_list[2]) / 1000
        
        z_real = amp * np.cos(phase) / (np.pi / 2) # scaling factor in birrp
        z_imag = amp * np.sin(phase) / (np.pi / 2) # scaling factor in birrp
        
        try:
            ant_dict[ant]
        except KeyError:
            ant_dict[ant] = np.zeros(24, 
                                     dtype=([('frequency', np.float),
                                             ('real', np.float),
                                             ('imaginary', np.float)]))
        ant_dict[ant][ff-1] = (f, z_real, z_imag)
        
for key in ant_dict.keys():
    df = pd.DataFrame(ant_dict[key])
    df.to_csv(r"d:\Peacock\MTData\Ant_calibrations\rsp_cal\{0}.csv".format(key),
              index=False, header=False, float_format='%.5e')
        
    