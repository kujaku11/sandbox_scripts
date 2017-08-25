# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 14:39:00 2017

@author: jpeacock
"""

import os
import numpy as np

fn_path = r"/mnt/hgfs/MTData/Umatilla/hf11/TS"

comp = 'hy'

fn_list = [os.path.join(fn_path, fn) for fn in os.listdir(fn_path)
           if fn.endswith(comp.upper())]

for fn in fn_list:
    print '-'*40
    print '    Reading {0}'.format(fn)
    with open(fn, 'r') as fid:
        header = fid.readline()

    x = np.loadtxt(fn, skiprows=1)
    x *= -1
    ts = x.astype('S18')

    print '    <-> Flipped Polarity'

    with open(fn, 'w') as fid:
        fid.write(header)
        fid.write('\n'.join(list(ts)))

    print '    Wrote {0}:'.format(fn)             