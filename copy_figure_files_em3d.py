# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 16:25:36 2015

@author: jpeacock
"""

import os
import shutil

fn = r"c:\Users\jpeacock\Documents\TexDocs\Presentations\EM3D6_2017\Peacock_EM3D6_2017.tex"

lv_figpath = r"c:\Users\jpeacock\Documents\LV\Figures"
figpath = r"c:\Users\jpeacock\Documents\TexDocs\Figures"

copy_path = r"c:\Users\jpeacock\zips\em3d_2017_peacock"

with open(fn, "r") as fid:
    lines = fid.readlines()

for line in lines:
    if line[0] == "%":
        continue
    if line.lower().find("includegraphics") > 0:
        line_str = line.replace("{", " ").replace("}", " ")
        line_list = line_str.strip().replace(";", "").split()
        fig_dir_path = os.path.dirname(line_list[-1][1:])
        fig_fn = os.path.basename(line_list[-1])
        fig_ext = os.path.splitext(fig_fn)[-1]
        if not fig_ext in [".jpg", ".pdf", ".png"]:
            continue

    #        elif fig_dir_path.find('lv') >=0:
    #            shutil.copy(os.path.join(lv_figpath, fig_fn),
    #                        os.path.join(copy_path, fig_fn))
    #            print 'Copied {0} to {1}'.format(os.path.join(lv_figpath, fig_fn),
    #                        os.path.join(copy_path, fig_fn))
    #        else:
    #            shutil.copy(os.path.join(figpath, fig_fn),
    #                        os.path.join(copy_path, fig_fn))
    #            print 'Copied {0} to {1}'.format(os.path.join(figpath, fig_fn),
    #                        os.path.join(copy_path, fig_fn))

    elif line.lower().find("animate") >= 0:
        print line
