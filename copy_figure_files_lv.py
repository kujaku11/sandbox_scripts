# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 16:25:36 2015

@author: jpeacock
"""

from pathlib import Path
import subprocess
import shutil

fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\TexDocs\mth5\mth5_manuscript_v5.tex")

fig_path = fn.parent

with open(fn, "r") as fid:
    lines = fid.readlines()

count = 1
for line in lines:
    if line[0] == "%":
        continue
    if line.lower().find("includegraphics") > 0:
        line_str = line.replace("{", " ").replace("}", " ")
        line_list = line_str.strip().replace(";", "").split()
        #fig_dir_path = os.path.dirname(line_list[-1][1:])
        fig_fn = fig_path.joinpath(line_list[-1])
        if fig_fn.suffix in [".pdf"]:
            
            numbered_fn = fig_path.joinpath(f"figure_{count:02}.pdf")
            shutil.copy(fig_fn, numbered_fn)
            count += 1
            print(f"Copied {fig_fn.name} to {numbered_fn.name}")
            
            std_out = subprocess.check_call(
                [
                    "magick",
                    "-density",
                    "300",
                    str(fig_fn),
                    "-flatten",
                    str(numbered_fn)[:-4] + ".jpg",
                ]
            )
            if std_out == 0:
                print(f"converted {fig_fn.name} to {numbered_fn.stem}")
