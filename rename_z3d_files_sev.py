# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 17:53:56 2017

@author: jpeacock
"""

import mtpy.usgs.zen as zen
import os

dir_path = r"d:\Peacock\MTData\sev"

ant_list = []
#for folder in os.listdir(dir_path):
for folder in ['MT008_rr']:

    folder_path = os.path.join(dir_path, folder)
    if os.path.isdir(folder_path):
        print '='*50
        print '     {0}'.format(folder)
        for fn in os.listdir(folder_path):
            fn_path = os.path.join(folder_path, fn)
            if os.path.isfile(fn_path) and fn_path.endswith('.Z3D'):
                zt = zen.Zen3D(fn=fn_path)
                zt.read_all_info()
#                if zt.df in [1024, '1024']:
#                    os.remove(fn_path)
#                    print 'Removed -> {0}'.format(fn_path)
                
                channel = zt.metadata.ch_cmp.upper()
                if channel in ['HX', 'HY', 'HZ']:
                    ant_list.append(zt.metadata.ch_number)
                
                st = zt.schedule.Time.replace(':','')
                sd = zt.schedule.Date.replace('-','')
                sv_fn = '{0}_{1}_{2}_{3}_{4}.Z3D'.format(folder, 
                                                         sd, 
                                                         st,
                                                         int(zt.df),
                                                         channel)
                os.rename(fn_path, os.path.join(folder_path, sv_fn))
                print 'renamed {0} to {1}'.format(fn_path,
                                                  os.path.join(folder_path, 
                                                               sv_fn))
                
ant_set = sorted(list(set(ant_list)))