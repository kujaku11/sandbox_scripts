# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 21:36:05 2018

@author: jpeacock-pr
"""

import os
import mtpy.usgs.zen as zen

survey_dir = r"c:\MT\SAGE_2017"

for station in os.listdir(survey_dir):
    station_dir = os.path.join(survey_dir, station)
    if os.path.isdir(station_dir):
        for chn in os.listdir(station_dir):
            chn_dir = os.path.join(station_dir, chn)
            if os.path.isdir(chn_dir):
                for fn in os.listdir(chn_dir):
                    if fn.lower().endswith(".z3d"):
                        z3d_obj = zen.Zen3D(os.path.join(chn_dir, fn))
                        z3d_obj.read_all_info()
                        channel = z3d_obj.metadata.ch_cmp.upper()
                        st = z3d_obj.schedule.Time.replace(":", "")
                        sd = z3d_obj.schedule.Date.replace("-", "")
                        sv_fn = "{0}_{1}_{2}_{3}_{4}.Z3D".format(
                            station, sd, st, int(z3d_obj.df), channel
                        )
                        os.rename(
                            os.path.join(chn_dir, fn), os.path.join(station_dir, sv_fn)
                        )
