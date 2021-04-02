# -*- coding: utf-8 -*-
"""
Created on Wed May 02 21:04:55 2018

@author: jpeacock-pr
"""

import os
import mtpy.usgs.zen as zen
import numpy as np

dir_path = r"c:\MT\Camas\cm211"
fn_list = [os.path.join(dir_path, fn) for fn in os.listdir(dir_path)
           if '256'in fn and fn.endswith('.Z3D')]

t_arr = np.zeros(5, 
                 dtype=[('comp', 'S3'),
                        ('start', np.int64),
                        ('stop', np.int64)])
                        
ts_list = []
for ii, fn in enumerate(sorted(fn_list[5:10])):
    z3d_obj = zen.Zen3D(fn)
    z3d_obj.read_z3d()
    dt_index = z3d_obj.ts_obj.ts.data.index.astype(np.int64)
    t_arr[ii]['comp'] = z3d_obj.metadata.ch_cmp.lower()
    t_arr[ii]['start'] = dt_index[0]
    t_arr[ii]['stop'] = dt_index[-1]
    ts_list.append(z3d_obj.ts_obj)

start = t_arr['start'].max()/10**9
stop = t_arr['stop'].min()/10**9
# figure out the max length of the array, getting the time difference into
# seconds and then multiplying by the sampling rate
ts_len = int((stop-start)*z3d_obj.df)

#ts_arr = np.zeros((5, ts_len))
temp_fn = os.path.join(os.path.dirname(z3d_obj.fn), 'ts_array.dat')
ts_mm = np.memmap(temp_fn,
                  dtype='int32',
                  mode='w+',
                  shape=(ts_len, 5))
for ii, ts in enumerate(ts_list):
    dt_index = ts.ts.data.index.astype(np.int64)/10**9
    index_0 = np.where(dt_index == start)[0][0]
    index_1 = np.where(dt_index == stop)[0][0]
    t_diff = ts_len-(index_1-index_0)
    print ii, t_diff
#    ts_arr[ii, 0:ts_len-t_diff] = ts.ts.data[index_0:index_1]
    ts_mm[0:ts_len-t_diff, ii] = ts.ts.data[index_0:index_1]
               