# -*- coding: utf-8 -*-
"""
Created on Tue Mar 08 11:55:19 2016

@author: jpeacock
"""

import os
import mtpy.utils.format as mtft

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\edi_files"
save_path = r"c:\Users\jpeacock\Documents\SaudiArabia\edi_files_z"
plot_path = r"c:\Users\jpeacock\Documents\SaudiArabia\resp_plots"

edi_list = [
    os.path.join(edi_path, edi) for edi in os.listdir(edi_path) if edi[-4:] == ".edi"
]

for edi in edi_list:
    edi_fid = file(edi, "r")
    edi_lines = edi_fid.readlines()
    if edi_lines[25][24] == "N":
        real_lon = edi_lines[25].strip().split()[4][4:]
        real_lon = "{0}:{1}".format(real_lon[0:2], real_lon[2:])
        dd = mtft._assert_position_format("long", real_lon)
        lon_str = mtft.convert_dms_tuple2string(mtft.convert_degrees2dms_tuple(dd))
        # replace the retarded long string output by phoenix
        # replace in header
        edi_lines[10] = "{0}{1}\n".format(edi_lines[10][0:9], lon_str)
        # replace in info
        edi_lines[25] = "{0}{1}  {2}".format(
            edi_lines[25][0:24], lon_str, edi_lines[25][34:]
        )
        # replace in definemeas
        edi_lines[61] = "{0}{1}\n".format(edi_lines[61][0:12], lon_str)
    new_fid = file(os.path.join(save_path, os.path.basename(edi)), "w")
    new_fid.write("".join(edi_lines))
    new_fid.close()
    edi_fid.close()
