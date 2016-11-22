# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 13:37:42 2016

@author: jpeacock
"""


import timeit

#def np_save():
#    import numpy as np
#    l = np.random.rand(256*60*60*8)
#    l_header = ','.join(list(('256.0', '1470097901', str(len(l)), '.2345', '.1230', '10.')))
#    np.savetxt(r"d:\Peacock\test.ex", l, fmt='%.8e', header=l_header)
#
#
#d = timeit.timeit(np_save, number=5)
#
#print 'np_save took {0:.2f} seconds'.format(d)
#def np_save():
#    import mtpy.usgs.zen as zen
#    z1 = zen.Zen3D(r"d:\Peacock\MTData\LV\mb401\mb401_20160614_015046_256_EX.Z3D")
#    z1.read_z3d()
#    z1.write_ascii_mt_file(save_fn=r"d:\Peacock\text_5.ex")
#
#
#d = timeit.timeit(np_save, number=1)
#
#print 'np_save took {0:.2f} seconds'.format(d)


def str_save():
    import mtpy.usgs.zen as zen
    import numpy as np
    z1 = zen.Zen3D(r"d:\Peacock\MTData\MonoBasin\MB_June2015\mb300\mb300_20150610_070056_4096_EY.Z3D")
    z1.read_z3d()
    l_header = ','.join(list(('256.0', '1470097901', str(len(z1.time_series)),
                              '.2345', '.1230', '10.')))
    ls = z1.convert_counts()/((100/100.)*(2*np.pi))
    ls = ls.astype('S18')
    with open(r"d:\Peacock\test_4.ex", 'w') as fid:
        fid.write(l_header+'\n')
        fid.write('\n'.join(ls))
        
d = timeit.timeit(str_save, number=1)

print 'str_save took {0:.2f} seconds'.format(d)        

#def fmt_save():
#    import numpy as np
#    l = np.random.rand(256*60*60*8)
#    l_header = ','.join(list(('256.0', '1470097901', str(len(l)), '.2345', '.1230', '10.')))
#    block_num = 0
#    block_len = 2**16
#    with open(r"d:\Peacock\test_3.ex", 'w') as fid:
#        fid.write(l_header+'\n')
#        while block_num*block_len <= len(l):
#            block = ['{0:.8e}'.format(ii) for ii in l[block_num*block_len:min((block_num+1)*block_len, len(l))]] 
#            fid.write('\n'.join(block))
#            block_num += 1
#        
#d = timeit.timeit(fmt_save, number=5)
#
#print 'fmt_save took {0:.2f} seconds'.format(d)   