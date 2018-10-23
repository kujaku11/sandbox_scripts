# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 10:17:28 2018

@author: jpeacock
"""

import subprocess
import os
import time

dir_path = r"c:\Users\jpeacock\Documents\TexDocs\Figures"

fn_list = [os.path.join(dir_path, fn) for fn in os.listdir(dir_path)
           if fn.endswith('.pdf')] 
fn_list.sort(key=os.path.getmtime, reverse=True)

def convert_pdt_to_jpg(fn):
    std_out = subprocess.check_call(['magick',
                                     'convert',
                                     '-density','300',
                                     fn,
                                     '-flatten',
                                     fn[:-4]+'.jpg'])
    print('--> Converted {0} to {1}'.format(os.path.basename(fn),
                                            os.path.basename(fn[:-4]+'.jpg')))
    return std_out

num_files = 14

for ii, fn in enumerate(fn_list):
    if num_files is not None and ii < num_files:
        std_out = convert_pdt_to_jpg(fn)
    elif num_files is not None and ii >= num_files:
        break
    elif num_files is None:        
        if os.path.getctime(fn) > round(time.time() - 5*60, -3):
            std_out = convert_pdt_to_jpg(fn)
        