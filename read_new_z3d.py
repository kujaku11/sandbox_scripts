# -*- coding: utf-8 -*-
"""
Created on Mon Sep 08 16:17:01 2014

@author: jpeacock-pr
"""

import os

fn = r"c:\MT\iMush\o010\09-03-2014\ZN0025\CH6\ZEUS3348.Z3D"
fid = file(fn, "rb")

header_len = 46
meta_len = 2

header_dict = {}
schedule_dict = {}
meta_dict = {}
for ii in range(header_len + meta_len):
    line = fid.readline()
    line_list = line.split("=")
    if len(line_list) == 2:
        key = line_list[0].strip().lower()
        value = line_list[1].strip().lower()
        if key.find("schedule") == 0:
            schedule_dict[key] = value
        else:
            header_dict[key] = value
    else:
        line_list = line.split("|")
        print line_list
        if len(line_list) < 5:
            line_list = line_list[0].split("|")
        if len(line_list) > 5:
            for ll in line_list:
                ll_list = ll.split(",")
                if len(ll_list) > 1:
                    key = ll[0].strip().lower()
                    value = ll[1].strip().lower()
                    meta_dict[key] = value

s_date = schedule_dict["schedule.date"].replace("-", "")
s_time = schedule_dict["schedule.time"].replace(":", "")
s_df = schedule_dict["schedule.s/r"]

new_fn = "{0}_{1}_{2}_{3}_{4}.Z3D".format("l010".upper(), s_date, s_time, s_df, s_comp)
print new_fn
