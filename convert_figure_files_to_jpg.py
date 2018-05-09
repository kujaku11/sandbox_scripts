# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 16:25:36 2015

@author: jpeacock
"""

import os
import subprocess

fn = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\Report\2018_umatilla_mt_peacock.tex"

fig_dir = os.path.dirname(fn)

with open(fn, 'r') as fid:
    lines = fid.readlines()

for line in lines:
    if line[0] == '%':
        continue
    if line.lower().find('includegraphics') > 0:
        line_str = line.replace('{', ' ').replace('}', ' ')
        line_list = line_str.strip().replace(';', '').split()
        fig_dir_path = os.path.dirname(line_list[-1][1:])
        fig_fn = os.path.basename(line_list[-1])
        if fig_fn.endswith('.pdf'):
            cfn = os.path.join(fig_dir, fig_fn)
            std_out = subprocess.check_call(['magick',
                                             '-density','300',
                                             cfn,
                                             cfn[:-4]+'.jpg'])
            if std_out == 0:
                print("converted {0} to jpg".format(fig_fn))
        
