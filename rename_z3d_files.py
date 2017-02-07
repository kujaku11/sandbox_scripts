# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 15:57:59 2017

@author: jpeacock
"""

import os
import mtpy.usgs.zen as zen

station_folder = r"d:\Peacock\MTData\MP_2017\mp205"

for fn in os.listdir(station_folder):
    if fn.endswith('.Z3D'):
        z3d_obj = zen.Zen3D(os.path.join(station_folder, fn))
        z3d_obj.read_all_info()
        
        station = os.path.basename(station_folder)
        channel = z3d_obj.metadata.ch_cmp.upper()
        st = z3d_obj.schedule.Time.replace(':','')
        sd = z3d_obj.schedule.Date.replace('-','')
        sv_fn = '{0}_{1}_{2}_{3}_{4}.Z3D'.format(station,
                                                 sd, 
                                                 st, 
                                                 int(z3d_obj.df),
                                                 channel)
        
        os.rename(os.path.join(station_folder, fn),
                  os.path.join(station_folder, sv_fn))
                  
        print 'renamed {0} to {1}'.format(fn, sv_fn)