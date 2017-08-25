# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 17:31:53 2017

@author: jpeacock
"""

import numpy as np

cov_fn = r"c:\Users\jpeacock\Documents\Montserrat\modem_inv\Inv04_dr\covariance.cov"

with open(cov_fn, 'r') as fid:
    lines = fid.readlines()
    
num_find = False
exceptions = False
east_find = False
north_find = False
count = 0
    
for line in lines:
    if line.find('+') >= 0 or line.find('|') >= 0:
        continue
    else:
        line_list = line.strip().split()
        if len(line_list) == 0:
            continue
        elif len(line_list) == 1 and num_find == False and \
             line_list[0].find('.') == -1:
            apply_num = int(line_list[0])
            num_find = True
        elif len(line_list) == 1 and num_find == True and \
             line_list[0].find('.') == -1:
             num_exceptions = int(line_list[0])
        elif len(line_list) == 1 and line_list[0].find('.') >= 0:
            smoothing_z = float(line_list[0])
        elif len(line_list) == 3:
            nx, ny, nz = [int(ii) for ii in line_list]
            cov_arr = np.zeros((nx, ny, nz), dtype=np.int)
            smoothing_east = np.zeros(ny)
            smoothing_north = np.zeros(nx)
            
        elif len(line_list) == 2:
            index_00, index_01 = [int(ii) for ii in line_list]
            count = 0
        elif line_list[0].find('.') >= 0 and north_find == False:
            smoothing_north = np.array(line_list, dtype=np.float)
            north_find = True
        elif line_list[0].find('.') >= 0 and north_find == True:
            smoothing_east = np.array(line_list, dtype=np.float)
            east_find = True
        elif north_find == True and east_find == True:
            line_list = np.array(line_list, dtype=np.int)
            
            cov_arr[count, :, index_00:index_01+1] = line_list.reshape((ny, 1))
            count += 1