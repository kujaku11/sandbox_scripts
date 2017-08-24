# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 16:59:27 2017

@author: jpeacock
"""

import os

dir_path = r"/home/jpeacock/Documents/ModEM/f90"
#find_str = 'RHS not allocated yet for copy_dataVec'
find_str = 'DataSpace'

for fn in os.listdir(dir_path):
    if os.path.isfile(os.path.join(dir_path, fn)) == True:
        if fn.endswith('.f90'):
            #print 'reading {0}'.format(fn)
            with open(os.path.join(dir_path, fn), 'r') as fid:
                fn_str = fid.read()
            if fn_str.find(find_str) > 0:
                print '*** FOUND in {0}'.format(fn)
                break
        else:
            continue
    if os.path.isdir(os.path.join(dir_path, fn)) == True:
        #print 'Looking in {0}'.format(os.path.join(dir_path, fn))
        for rfn in os.listdir(os.path.join(dir_path, fn)):
            if os.path.isfile(os.path.join(dir_path, fn, rfn)) == True:
                if rfn.endswith('.f90'):
                    #print 'reading {0}'.format(rfn)
                    with open(os.path.join(dir_path, fn, rfn), 'r') as fid:
                        fn_str = fid.read()
                    if fn_str.find(find_str) > 0:
                        print '*** FOUND in {0}'.format(os.path.join(fn, rfn))
                        break
                else:
                    continue
            