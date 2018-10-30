# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 17:39:21 2018

@author: jpeacock
"""

import os
import shutil
import mtpy.usgs.zen as zen

#main_dir = r"/media/jpeacock/My Passport/iMUSH"
main_dir = r"d:\Peacock\MTData\iMUSH_Zen_samples\imush"

#notes = ['# Notes for stations']
         
station = 'F013-5'
#station_dir = r"/media/jpeacock/My Passport/iMUSH/OSU_2015/H021_revisit"
station_dir = r"d:\Peacock\MTData\iMUSH_Zen_samples\F0135_Zen18"

# make a folder in the main directory to save to
sv_path = os.path.join(main_dir, station)
if not os.path.exists(sv_path):
    os.mkdir(sv_path)
print('--- {0}'.format(sv_path))
# look for all Z3D files within a station folder
for root, folders, files in os.walk(station_dir):
    for fn in files:
        if fn.lower().endswith('.z3d'):
            fn_path = os.path.join(root, fn)
            # skip the small files
            if os.stat(fn_path).st_size < 300000L:
                print('---> Skipping {0} too small {1}'.format(fn, os.stat(fn_path).st_size))
                continue
            if fn.count('_') == 4:
                sv_fn = '_'.join([station]+fn.split('_')[1:])
                shutil.move(fn_path, 
                            os.path.join(sv_path, sv_fn))
            else:
                # read in just the metadata
                z_obj = zen.Zen3D(fn_path)
                z_obj.read_all_info()
                z_obj.station = station
#                try:
                channel = z_obj.metadata.ch_cmp.upper()
#                except AttributeError:
##                    notes.append('***CHECK {0}'.format(fn_path))
#                    continue
                st = z_obj.schedule.Time.replace(':','')
                sd = z_obj.schedule.Date.replace('-','')
                # make a new useful file name
                sv_fn = '{0}_{1}_{2}_{3}_{4}.Z3D'.format(station, 
                                                         sd, 
                                                         st,
                                                         int(z_obj.df),
                                                         channel)
                # rename that file instead of copy, way faster
                shutil.move(fn_path, 
                            os.path.join(sv_path, sv_fn))
#                            os.rename(fn_path, 
#                                      os.path.join(station_path, sv_fn))
        elif 'mtft24.cfg' in fn:
            shutil.move(os.path.join(root, fn),
                        os.path.join(sv_path, 
                                     '{0}_mtft24.cfg'.format(station)))
        else:
            continue
    
### write out notes
#with open(os.path.join(main_dir, 'station_notes.txt'), 'w') as fid:
#    fid.write('\n'.join(notes))
                    
                
