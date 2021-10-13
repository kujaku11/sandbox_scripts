# -*- coding: utf-8 -*-
"""
Created on Mon Sep 08 15:43:49 2014

@author: jpeacock-pr
"""

import mtpy.usgs.zen as zen
import os
import shutil

dirpath = r"c:\MT\iMush\geq010"

channel_dict = {"ch1": "ex", "ch2": "ey", "ch4": "hx", "ch5": "hy", "ch6": "hz"}
station = "geq010"
for zfn in os.listdir(dirpath):
    if zfn[-3:] == "Z3D":
        z_fn = os.path.join(dirpath, zfn)
        z1 = zen.Zen3D(z_fn)
        comp = z_fn[-6:-4].lower()
        try:
            z1.get_info()
            s_date = z1.start_date.replace("-", "")
            s_time = z1.start_time.replace(":", "")
            s_station = station
            s_comp = comp.upper()
            s_sr = int(z1.df)
            new_fn = "{0}_{1}_{2}_{3}_{4}.Z3D".format(
                s_station.upper(), s_date, s_time, s_sr, s_comp
            )
            new_z_fn = os.path.join(dirpath, new_fn)

            shutil.copy(z_fn, new_z_fn)
            print "renamed {0} to \n{1}".format(z_fn, new_z_fn)

        except KeyError:
            print "-" * 50
            print "   {0}".format(z_fn)
            fid = file(z_fn, "rb")
            header_len = 46
            meta_len = 3

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
                    if len(line_list) > 5:
                        for ll in line_list:
                            ll_list = ll.split(",")
                            if len(ll_list) > 1:
                                key = ll_list[0].strip().lower()
                                value = ll_list[1].strip().lower()
                                meta_dict[key] = value
            s_station = station
            s_date = schedule_dict["schedule.date"].replace("-", "")
            s_time = schedule_dict["schedule.time"].replace(":", "")
            s_df = schedule_dict["schedule.s/r"]
            s_comp = comp.upper()

            new_fn = "{0}_{1}_{2}_{3}_{4}.Z3D".format(
                s_station.upper(), s_date, s_time, s_df, s_comp
            )
            new_z_fn = os.path.join(dirpath, new_fn)

            shutil.copy(z_fn, new_z_fn)
            print "renamed {0} to \n        {1}".format(z_fn, new_z_fn)
