# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 10:48:12 2015

@author: jpeacock-pr
"""

import os
import datetime

lib_path = r"c:\Python27\Lib\site-packages\mtpy"
git_path = r"c:\Users\jpeacock-pr\Documents\GitHub\mtpy\mtpy"
tab = ' '*4

for folder in os.listdir(lib_path):
    print '{0}{1:^17}{0}'.format('='*10, folder)
    if os.path.isdir(os.path.join(lib_path, folder)) is True and \
       os.path.isdir(os.path.join(git_path, folder)) is True:
        for fn_lib in os.listdir(os.path.join(lib_path, folder)):
            for fn_git in os.listdir(os.path.join(git_path, folder)):
                if fn_lib == fn_git and fn_lib[-3:] == '.py':
                    
                    fn_git_path = os.path.join(git_path, folder, fn_git)
                    fn_lib_path = os.path.join(lib_path, folder, fn_lib)
                    
                    stat_git = os.stat(fn_git_path)
                    stat_lib = os.stat(fn_lib_path)
                    
                    dt_git = datetime.datetime.ctime(
                             datetime.datetime.fromtimestamp(stat_git.st_mtime))
                    dt_lib = datetime.datetime.ctime(
                             datetime.datetime.fromtimestamp(stat_lib.st_mtime))

                    # check modification date                                     
                    if stat_git.st_size != stat_lib.st_size:
                        print '**** {0}'.format(fn_lib)
#                        print '{0}Size Git: {1:<15}'.format(tab, 
#                                                            stat_git.st_size) 
#                        print '{0}Size Lib: {1:<15}'.format(tab, 
#                                                            stat_lib.st_size) 
                        
#                        print '\tDate Git: {0:<15}'.format(stat_git.st_mtime) 
#                        print '\tDate Lib: {0:<15}'.format(stat_lib.st_mtime) 
#                        if stat_git.st_mtime > stat_lib.st_mtime:
#                            print '  ->Date Git: {1:<15}'.format(tab, dt_git) 
#                            print '{0}Date Lib: {1:<15}'.format(tab, dt_lib)
                        if stat_git.st_mtime < stat_lib.st_mtime:
                            print '{0}Date Git: {1:<15}'.format(tab, dt_git) 
                            print '  ->Date Lib: {1:<15}'.format(tab,dt_lib)