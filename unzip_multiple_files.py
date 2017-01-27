# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 16:07:48 2017

@author: jpeacock
"""

import subprocess
import os
import time

dir_path = r"d:\Peacock\MTData\sev"

zip_files = [os.path.join(dir_path, zip_fn) for zip_fn in os.listdir(dir_path)
             if zip_fn.endswith('.zip')]
                 
log_file = open(os.path.join(dir_path, 'unzip.log'), 'w')
for zip_file in zip_files:
    print '='*50
    print os.path.basename(zip_file)
    print '    start time: {0}'.format(time.ctime())    
    new_dir = os.path.join(dir_path, os.path.basename(zip_file[:-4]))
    pro = subprocess.Popen(["unzip", zip_file, "-d", new_dir],
                           stdin=subprocess.PIPE,
                           stdout=log_file,
                           stderr=log_file)                 
    pro.communicate()
    print '    end time:   {0}'.format(time.ctime()) 
    
log_file.close()