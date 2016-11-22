# -*- coding: utf-8 -*-
"""
Created on Fri Sep 09 18:12:40 2016

@author: jpeacock
"""


import timeit
def resample_0():
    import mtpy.usgs.zen as zen
    import numpy as np    
    z1 = zen.Zen3D(r"d:\Peacock\MTData\LV\mb401\mb401_20160613_223016_256_EX.Z3D")
    z1.read_z3d()
    t1 = z1.time_series
    t2 = zen.sps.decimate(t1, 16)
#    w = zen.sps.slepian(2**8-1, 16./256)
#    p2 = np.ceil(np.log2(t1.size))
#    t0 = np.zeros(int(2**p2))
#    t0[0:t1.size] = t1
#    
#    wt = zen.sps.fftconvolve(t0, w, mode='same')[np.arange(0, t1.size, 256/16)]
#    t2 = zen.sps.resample(t1, t1.size/16, window='hamming')
    
print np.mean(timeit.timeit(resample_0, number=10))

