# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 16:25:36 2015

@author: jpeacock
"""

import os
import subprocess
import shutil

fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\jvgr\2019_jvgr_geysers_peacock_v3.tex"

convert = False
rename = True

fig_dir = os.path.dirname(fn)
count = 1

index = 0

with open(fn, "r") as fid:
    line = "adfa"

    while line != "":
        try:
            line = fid.readline()
            # print(line)
            if line.lower().find("includegraphics") >= 0:
                line_str = line.replace("{", " ").replace("}", " ")
                line_list = line_str.strip().replace(";", "").split()
                fig_dir_path = os.path.dirname(line_list[-1][1:])
                fig_basename = os.path.basename(line_list[-1])
                figure_fn = os.path.join(fig_dir, fig_basename)
                print("--> Found {0}".format(fig_basename))
                if convert:
                    if fig_basename.endswith(".pdf"):
                        std_out = subprocess.check_call(
                            [
                                "magick",
                                "-density",
                                "300",
                                figure_fn,
                                "-flatten",
                                figure_fn[:-4] + ".jpg",
                            ]
                        )

                    if std_out == 0:
                        print("converted {0} to jpg".format(fig_basename))
                if rename:
                    fig_num = "figure_{0:02}.pdf".format(count)
                    shutil.copy(figure_fn, os.path.join(fig_dir, fig_num))
                    print("Copied {0} to {1}".format(fig_basename, fig_num))
                    count += 1

            index += 1
        except UnicodeDecodeError:
            fid.readline()
            print(index, line)

    # lines = fid.readlines()

# for line in lines:
#     if line[0] == '%':
#         continue
#     if line.lower().find('includegraphics') > 0:
#         line_str = line.replace('{', ' ').replace('}', ' ')
#         line_list = line_str.strip().replace(';', '').split()
#         fig_dir_path = os.path.dirname(line_list[-1][1:])
#         fig_fn = os.path.basename(line_list[-1])
#         if fig_fn.endswith('.pdf'):
#             cfn = os.path.join(fig_dir, fig_fn)
#             std_out = subprocess.check_call(['magick',
#                                              '-density','300',
#                                              cfn,
#                                              cfn[:-4]+'.jpg'])
#             if std_out == 0:
#                 print("converted {0} to jpg".format(fig_fn))
