# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd

ant_fn = r"/mnt/hgfs/MT/amtant.cal"

birrp = False

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
        amp = float(line_list[1])
        ### Zonge uses milliradians for what ever reason
        phase = float(line_list[2]) / 1000
        
        z_real = amp * np.cos(phase) #
        z_imag = amp * np.sin(phase) #
        
        try:
            ant_dict[ant]
        except KeyError:
            ant_dict[ant] = np.zeros(25, 
                                     dtype=([('frequency', np.float),
                                             ('real', np.float),
                                             ('imaginary', np.float)]))
            if birrp:
                ### BIRRP now expects the first line to be a scaling factor
                ### need to set this to 1
                ant_dict[ant][0] = (1, 1, 1) ### needed for birrp
                
        ant_dict[ant][ff] = (f, z_real, z_imag)
        
for key in ant_dict.keys():
    df = pd.DataFrame(ant_dict[key])
    df.to_csv(r"d:\Peacock\MTData\Ant_calibrations\rsp_cal\{0}.csv".format(key),
              index=False, header=False, float_format='%.5e')
        
    