# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 16:25:36 2015

@author: jpeacock
"""

import os
import shutil

fn = r"c:\Users\jpeacock\Documents\TexDocs\Presentations\Berkeley_2017\Peacock_berkeley_2017.tex"

lv_figpath = r"c:\Users\jpeacock\Documents\LV\Figures"
fig_path = r"c:\Users\jpeacock\Documents\TexDocs\Figures"
msh_path = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\Report"

copy_path = r"c:\Users\jpeacock\zips\berkeley_2017_peacock"
if not os.path.exists(copy_path):
    os.mkdir(copy_path)

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
        fig_ext = os.path.splitext(fig_fn)[-1]
        if not fig_ext in ['.jpg', '.pdf', '.png']:
            continue
    

        elif fig_dir_path == 'lvfigpath':
            shutil.copy(os.path.join(lv_figpath, fig_fn),
                        os.path.join(copy_path, fig_fn)) 
#            print 'Copied {0} to {1}'.format(os.path.join(lv_figpath, fig_fn),
#                        os.path.join(copy_path, fig_fn)) 
        elif fig_dir_path == 'figpath':
            shutil.copy(os.path.join(fig_path, fig_fn),
                        os.path.join(copy_path, fig_fn)) 
#            print 'Copied {0} to {1}'.format(os.path.join(fig_path, fig_fn),
#                        os.path.join(copy_path, fig_fn)) 
        elif fig_dir_path == 'mshfigpath':
            shutil.copy(os.path.join(msh_path, fig_fn),
                        os.path.join(copy_path, fig_fn)) 
#            print 'Copied {0} to {1}'.format(os.path.join(msh_path, fig_fn),
#                        os.path.join(copy_path, fig_fn)) 

    elif line.lower().find('animate') >= 0:
        print '-'*72
        print line
        print '-'*72
