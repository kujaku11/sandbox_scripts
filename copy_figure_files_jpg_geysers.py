# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 16:25:36 2015

@author: jpeacock
"""

import os
import subprocess

fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\jvgr\2019_jvgr_geysers_peacock.tex"

fig_dir = os.path.dirname(fn)

lines = []
count = 322
ii = 0
with open(fn, "r") as fid:
    while ii < count:
        try:
            lines.append(fid.readline())
        except UnicodeDecodeError:
            continue
        ii += 1

for line in lines:
    if len(line) == 0:
        continue
    if line[0] == "%":
        continue
    if line.lower().find("includegraphics") > 0:
        line_str = line.replace("{", " ").replace("}", " ")
        line_list = line_str.strip().replace(";", "").split()
        fig_dir_path = os.path.dirname(line_list[-1][1:])
        fig_fn = os.path.basename(line_list[-1])
        if fig_fn.endswith(".pdf"):
            cfn = os.path.join(fig_dir, fig_fn)
            std_out = subprocess.check_call(
                ["magick", "-density", "300", cfn, "-flatten", cfn[:-4] + ".jpg"]
            )
            if std_out == 0:
                print("converted {0} to jpg".format(fig_fn))
